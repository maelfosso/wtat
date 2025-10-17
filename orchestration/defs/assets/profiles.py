import dagster as dg
from dagster_duckdb import DuckDBResource
import time
import pandas as pd
from orchestration.llm.llm_service import LLMService
from orchestration.helpers.profiles.transform import transform_profile_data
from orchestration.helpers.profiles.cleaning import (
  parse_age, normalize_sex, normalize_and_map_country,
  normalize_region, fill_region_from_village, clean_village,
  normalize_sector, normalize_marital_status, clean_number_of_children,
  detect_illness, normalize_illness, list_to_string,
  extract_height_range, extract_weight_range, clean_physical_appearance,
  prepare_for_embedding,
  remove_suffixes
)
from orchestration.defs.resources import ClickHouseResource

@dg.asset(
  deps=["ads"],
  required_resource_keys={"llm", "database"}
)
async def extracted_profiles(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
  llm: LLMService = context.resources.llm
  database: DuckDBResource = context.resources.database

  query = """
    SELECT * FROM ads
  """
  with database.get_connection() as conn:
    ads = conn.execute(query).fetch_df()

  context.log.info(f"Processing {len(ads)} for profiles extractions")

  extracted_profiles = []
  for index, ad in ads.iterrows():
    ad_id = ad['id']
    ad_text = ad['ad']

    context.log.info(f"Processing AD {ad_id}: {ad_text[:100]}...")
    with database.get_connection() as conn:
      conn.execute("""
        UPDATE ads
        SET extraction_status = 'PENDING'
        WHERE id = ?
      """, [ad_id])

    start_time = time.time()
    try:
      try:
        llm_results = await llm.extract_profile_from_single_ad(ad, context=context)
        context.log.info("LLM RESULTS")
        context.log.info(llm_results)
        # if llm_results and len(llm_results) > 0:
        #   llm_result = llm_results[0]
        #   context.log.info("Result for LLM extraction: ", llm_result)
        # else:
        #   raise Exception("No LLM results returned")
        llm_result = llm_results
      except Exception as e:
        extraction_time = time.time() - start_time
        context.log.error(f"An error occur : after {extraction_time}\n {str(e)}")

        with database.get_connection() as conn:
          conn.execute("""
            UPDATE ads
            SET extraction_status = 'FAILED', extraction_time = ?
            WHERE id = ?
          """, [str(extraction_time), ad_id])

      context.log.info("Processing LLM Result, the profile extracted")
      context.log.info(llm_result)
      ad_profiles = llm_result.get('profiles', {})
      extraction_time = time.time() - start_time
      if not ad_profiles.get('advertiser') or not ad_profiles.get('desired'):
        with database.get_connection() as conn:
          conn.execute("""
            UPDATE ads
            SET extraction_status = 'FAILED', extraction_time = ?
            WHERE id = ?
          """, [str(extraction_time), ad_id])

        context.log.info(f"Incomplete profile data for AD {ad_id}")
      else:
        with database.get_connection() as conn:
          conn.execute("""
            UPDATE ads
            SET extraction_status = 'SUCCESS', extraction_time = ?
            WHERE id = ?
          """, [str(extraction_time), ad_id])

        extracted_profiles.append(llm_result)
        context.log.info("AD %s processed successfully in batch", ad_id)
      context.log.info("AD %s processed successfully", ad_id)
    except Exception as e:
      context.log.info(f"error occurred: {e}")

  return dg.MaterializeResult(
      metadata={
        "Nombre d'annonces traitées": len(ads),
        "Profils extraits": len(extracted_profiles)
      },
      value=extracted_profiles
    )

@dg.asset(
  deps=["extracted_profiles"],
  required_resource_keys={"llm", "database"}
)
def inserted_profiles(
  context: dg.AssetExecutionContext,
  extracted_profiles: list
) -> dg.MaterializeResult:
  database: DuckDBResource = context.resources.database

  extracted_profiles = extracted_profiles

  create_table_query = """
    CREATE TABLE IF NOT EXISTS profiles (
      id INTEGER PRIMARY KEY,
      ad_id INTEGER,
      profile_type VARCHAR(10),
      name VARCHAR(100),
      religion VARCHAR(150),
      age VARCHAR(120),
      sex VARCHAR(110),
      country_of_residence VARCHAR[],
      country_of_origin VARCHAR(100),
      region_of_origin VARCHAR(100),
      village_of_origin VARCHAR(100),
      sector_of_activity VARCHAR(100),
      marital_status VARCHAR(150),
      has_children BOOLEAN,
      number_of_children TEXT,
      qualities VARCHAR[],
      values VARCHAR[],
      defects VARCHAR[],
      interests VARCHAR[],
      height VARCHAR(120),
      weight VARCHAR(120),
      physical_appearance TEXT,
      economic_situation TEXT,
      education_level TEXT,
      illness TEXT,
      relationship_goal TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE (ad_id, profile_type)
    )
    """
    
  with database.get_connection() as conn:
    conn.execute(create_table_query)
    
  all_profiles = []
  for profile in extracted_profiles:
    profile_to_insert = transform_profile_data(profile)
    all_profiles.extend(profile_to_insert)

  insert_query = """
    INSERT OR IGNORE INTO profiles (
        id, ad_id, profile_type, name, religion, age, sex, country_of_residence,
        country_of_origin, region_of_origin, village_of_origin, sector_of_activity,
        marital_status, has_children, number_of_children, qualities, values,
        defects, interests, height, weight, physical_appearance, economic_situation,
        education_level, illness, relationship_goal
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    """
  
  with database.get_connection() as conn:
  
    values = []
    for profile in all_profiles:
      values.append([
        profile['id'],
        profile['ad_id'],
        profile['profile_type'],
        profile['name'],
        profile['religion'],
        profile['age'],
        profile['sex'],
        profile['country_of_residence'],
        profile['country_of_origin'],
        profile['region_of_origin'],
        profile['village_of_origin'],
        profile['sector_of_activity'],
        profile['marital_status'],
        profile['has_children'],
        profile['number_of_children'],
        profile['qualities'],
        profile['values'],
        profile['defects'],
        profile['interests'],
        profile['height'],
        profile['weight'],
        profile['physical_appearance'],
        profile['economic_situation'],
        profile['education_level'],
        profile['illness'],
        profile['relationship_goal']
    ])
      
    conn.executemany(insert_query, values)
  
  return dg.MaterializeResult(
    metadata={
      "Profile Inserted": len(all_profiles),
      "Adversiter Profiles": len([p for p in all_profiles if p['profile_type'] == 'ADVERTISER']),
      "Desired Profiles": len([p for p in all_profiles if p['profile_type'] == 'DESIRED'])
    }
  )

@dg.asset(
  deps=["inserted_profiles"],
  required_resource_keys={"clickhouse", "database"}
)
def cleaned_profiles(
  context: dg.AssetExecutionContext
) -> dg.MaterializeResult:
  context.log.info("Starting cleaning profiles...")

  database: DuckDBResource = context.resources.database
  clickhouse: ClickHouseResource = context.resources.clickhouse

  with database.get_connection() as conn:
    profiles = conn.execute("""
      SELECT * FROM profiles
    """).fetch_df()

  df = profiles.copy()

  age_parsed = df["age"].apply(parse_age).apply(pd.Series)
  age_parsed.columns = ["age_min", "age_max", "age_mean"]
  df = pd.concat([df.drop(columns=["age"]), age_parsed], axis=1)

  df["sex"] = df["sex"].apply(normalize_sex)

  df["country_of_residence_cleaned"] = df["country_of_residence"].apply(normalize_and_map_country)
  df["country_of_origin_cleaned"] = df["country_of_origin"].apply(normalize_and_map_country)

  df["region_normalized"] = df["region_of_origin"].apply(normalize_region)
  df["region_normalized"] = df.apply(fill_region_from_village, axis=1)
  df["village_cleaned"] = df["village_of_origin"].apply(clean_village)

  df["sector"] = df["sector_of_activity"].apply(normalize_sector)

  df["marital_status_normalized"] = df["marital_status"].apply(normalize_marital_status)

  df["number_of_children_cleaned"] = df["number_of_children"].apply(clean_number_of_children)
  df["has_children_cleaned"] = df["number_of_children_cleaned"].apply(lambda x: x > 0)

  df["has_illness"] = (
    df["illness"].apply(detect_illness) |
    df["marital_status"].apply(detect_illness)
  )
  df["illness_cleaned"] = df["illness"].apply(normalize_illness)

  for col in ["qualities", "values", "defects", "interests"]:
    df[f"{col}_cleaned"] = df[col].apply(list_to_string).apply(prepare_for_embedding)

  height_df = df["height"].apply(extract_height_range).apply(pd.Series)
  height_df.columns = ["height_min", "height_max", "height_mean"]

  weight_df = df["weight"].apply(extract_weight_range).apply(pd.Series)
  weight_df.columns = ["weight_min", "weight_max", "weight_mean"]

  df = pd.concat([df.drop(columns=["height", "weight"]), height_df, weight_df], axis=1)


  df["physical_appearance_cleaned"] = df["physical_appearance"].apply(clean_physical_appearance)
  df["economic_cleaned"] = df["economic_situation"].apply(prepare_for_embedding)
  df["education_level_cleaned"] = df["education_level"].apply(prepare_for_embedding)
  df["relationship_goal_cleaned"] = df["relationship_goal"].apply(prepare_for_embedding)

  cols_to_drop = [
    "region_of_origin", "village_of_origin", "sector_of_activity",
    "marital_status", "number_of_children", "has_children",
    "illness", "height", "weight", "economic_situation", "country_of_origin", "country_of_residence",
    "education_level", "relationship_goal", "physical_appearance",
    "qualities", "values", "defects", "interests"
  ]
  df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

  df = remove_suffixes(df)
  ordered_cols = [
    "id", "ad_id", "profile_type", "name", "sex",
    "age_min", "age_max", "age_median",
    "country_of_residence", "country_of_origin",
    "region", "village", "sector", "marital_status",
    "number_of_children", "has_children",
    "illness", "has_illness",
    "qualities", "values",
    "defects", "interests",
    "height_min", "height_max", "height_mean",
    "weight_min", "weight_max", "weight_mean",
    "physical_appearance", "economic",
    "education_level", "relationship_goal",
    "created_at"
  ]
  df = df[[col for col in ordered_cols if col in df.columns]]

  # === Aperçu du résultat === #
  context.log.info(f"✅ Shape: {df.shape}")
  context.log.info(f"✅ Colonnes: {list(df.columns)}")
  context.log.info(df.head())
  context.log.info(f"DataFrame types before insert:\n{df.dtypes}")

  query = """
    CREATE OR REPLACE cleaned_profiles
    SELECT *
    FROM df
  """
  with database.get_connection() as conn:
    conn.execute(query)

  return dg.MaterializeResult(
    metadata={
      "Raw Profile Shape": {
        "rows": profiles.shape[0],
        "columns": profiles.shape[1]
      },
      "Cleaned Profile Shape": {
        "rows": df.shape[0],
        "columns": df.shape[1],
      },
      "Cleaned Profiles columns": df.columns.to_list()
    }
  )
