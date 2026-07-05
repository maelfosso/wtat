import dagster as dg
from dagster_duckdb import DuckDBResource
import time
from datetime import datetime 
import json
import pandas as pd
import asyncio
from .ads import ads
from ...adapters.repository import Repository
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

@dg.asset(
  deps=[ads],
  required_resource_keys={"llm", "database"},
  retry_policy=dg.RetryPolicy(
    max_retries=3,
    delay=60,
    backoff=dg.Backoff.EXPONENTIAL
  )
)
async def profiles(
  context: dg.AssetExecutionContext
) -> dg.MaterializeResult:
  """Extract profiles using LLM from ads and save them into DuckDB"""
  
  llm: LLMService = context.resources.llm
  database: DuckDBResource = context.resources.database

  with database.get_connection() as conn:
    repo = Repository(conn)
    ads_df = repo.fetch_ads_to_process()

  if ads_df.empty:
    return dg.MaterializeResult(
      metadata={
        "ads_processed": 0,
        "extracted": 0
      }
    )

  context.log.info(f"Extraction LLM pour {len(ads_df)} annonces")
  sem = asyncio.Semaphore(10)

  async def one(ad):
    ad_id, t0 = ad["ad_id"], time.time()

    try:
      with database.get_connection() as conn:
        repo = Repository(conn)
        repo.ad_extraction_started(ad_id)

      profiles = await llm.extract_profile_from_single_ad(ad, context=context)
      dt = time.time() - t0

      with database.get_connection() as conn:
        repo = Repository(conn)
        repo.ad_extraction_success(ad_id, profiles, dt)
      
      return {"ad_id": ad_id, "status": "success", "time": dt}
    except Exception as e:
      dt = time.time() - t0

      with database.get_connection() as conn:
        repo = Repository(conn)
        repo.ad_extraction_failed(ad_id, dt)

      context.log.warning(f"❌ {ad_id}: {str(e)[:200]}")
      return {"ad_id": ad_id, "status": "failed", "time": dt}

  async def bounded(row):
    async with sem:
      return await one(row)
    
  results = await asyncio.gather(*[bounded(r) for _, r in ads_df.iterrows()],
                                 return_exceptions=True)
  ok = [r for r in results if isinstance(r, dict) and r["status"] == "success"]
  ko = [r for r in results if isinstance(r, dict) and r["status"] == "failed"]
  
  TARGET = 0.95
  rate = len(ok) / len(ads_df)
  context.log.info(f"Succes: {rate:.1%} ({len(ok)}/{len(ads_df)})")
  if rate < TARGET:
    raise dg.Failure(f"Taux {rate:.1%} < 95%. Echecs: {len(ko)}")

  return dg.MaterializeResult(
    metadata={
      "ads_processed": dg.MetadataValue.int(len(ads_df)),
      "success": dg.MetadataValue.int(len(ok)),
      "failed": dg.MetadataValue.int(len(ko)),
      "avg_extraction_time_sec": dg.MetadataValue.float(
        (sum(r["time"] for r in ok) / len(ok)) if ok else 0.0
      )
    }
  )

@dg.asset_check(
  asset=profiles,
  blocking=True
)
def profile_success_rate_check(
  context: dg.AssetCheckExecutionContext,
  database: DuckDBResource
) -> dg.AssetCheckResult:
  """
  Check that the success rate of the LLM if >= 95%
  Otherwise, downstream asset are blocked
  """
  
  with database.get_connection() as conn:
    result = conn.execute("""
      SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN extraction_status = 'SUCCESS' THEN 1 ELSE 0 END) AS success
      FROM ads
    """).fetchone()

  total, success = result
  success_rate = (success / total) * 100 if total > 0 else 0.0

  TARGET = 95.0
  passed = success_rate >= TARGET

  return dg.AssetCheckResult(
    passed=passed,
    metadata={
      "success_rate_percent": dg.MetadataValue.float(success_rate),
      "threshold_percent": dg.MetadataValue.float(TARGET),
      "total_processed": dg.MetadataValue.int(total),
      "success_count": dg.MetadataValue.int(success),
      "message": (
        f"✅ {success_rate:.1f}% >= {TARGET}% -> downstream authorized"
        if passed else
        f"❌ {success_rate:.1f}% < {TARGET}% -> downstream blocked (run profiles asset again)"
      )
    }
  )

@dg.asset(
  deps=[profiles]
)
def records(
  context: dg.AssetExecutionContext,
  database: DuckDBResource
) -> dg.MaterializeResult:
  """Transform desired, advertiser JSON into tabular data"""
  
  with database.get_connection() as conn:
    raw_df = conn.execute("""
      SELECT ad_id, advertiser, desired
      FROM raw_profiles
      WHERE extraction_error IS NULL                    
    """).fetch_df()

  context.log.info(f"Processing {len(raw_df)} profiles JSON -> Tabular")

  flat_rows = []
  for _, row in raw_df.iterrows():
    transformed = transform_profile_data({
      "ad_id": row["ad_id"],
      "profiles": {
        "advertiser": json.loads(row["advertiser"]),
        "desired": json.loads(row["desired"])
      }
    })

    flat_rows.extend(transformed)
  
  flat_df = pd.DataFrame(flat_rows)
  if flat_df.empty:
    context.log.warning("No profil transformed")
    return dg.MaterializeResult(metadata={
      "rows_inserted": 0
    })
  
  context.log.info(f"✅ {len(flat_df)} tabular rows generated ({len(flat_df[flat_df['profile_type'] == 'ADVERTISER'])} ADVERTISER), {len(flat_df[flat_df['profile_type'] == 'DESIRED'])}")

  with database.get_connection() as conn:
    columns_def = ", ".join([
      f"{col} VARCHAR" if flat_df[col].dtype == "object" else 
      f"{col} INTEGER" + (" PRIMARY KEY" if col == "id" else "") if pd.api.types.is_integer_dtype(flat_df[col]) else
      f"{col} DOUBLE" if pd.api.types.is_float_dtype(flat_df[col]) else
      f"{col} BOOLEAN" if pd.api.types.is_bool_dtype(flat_df[col]) else
      f"{col} VARCHAR"
      for col in flat_df.columns
    ])

    conn.execute(f"""
      CREATE OR REPLACE TABLE profiles (
        {columns_def},
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """)

    flat_df['created_at'] = datetime.now()
    conn.execute("INSERT INTO profiles SELECT * FROM flat_df")
    
  return dg.MaterializeResult(
    metadata={
      "input_profiles": len(raw_df),
      "output_rows": len(flat_df),
      "advertiser_count": len(flat_df[flat_df["profile_type"] == "ADVERTISER"]),
      "desired_count": len(flat_df[flat_df["profile_type"] == "DESIRED"]),
    }
  )

@dg.asset(
  deps=[records]
)
def cleaned_profiles(
  context: dg.AssetExecutionContext,
  database: DuckDBResource
) -> dg.MaterializeResult:
  """Cleaning profiles"""

  with database.get_connection() as conn:
    profiles = conn.execute("""
      SELECT * FROM profiles
    """).fetch_df()

  df = profiles.copy()

  age_parsed = df["age"].apply(parse_age).apply(pd.Series)
  age_parsed.columns = ["age_min", "age_max", "age_mean"]
  df = pd.concat([df.drop(columns=["age"]), age_parsed], axis=1)

  df["sex"] = df["sex"].apply(normalize_sex)

  country_of_residence_cleaned = df["country_of_residence"].apply(normalize_and_map_country)
  country_of_residence_df = pd.DataFrame([
    x if isinstance(x, dict) and len(x) == 2 else {'country': None, 'continent': None}
    for x in country_of_residence_cleaned
  ])
  country_of_residence_df.columns = ['country_of_residence_cleaned', 'continent_of_residence_cleaned']
  df = pd.concat([df.drop(columns=['country_of_residence']), country_of_residence_df], axis=1)

  country_of_origin_cleaned = df["country_of_origin"].apply(normalize_and_map_country)
  country_of_origin_df = pd.DataFrame([
    x if isinstance(x, dict) and len(x) == 2 else {'country': None, 'continent': None}
    for x in country_of_origin_cleaned
  ])
  for x in country_of_origin_cleaned.head(n=10):
    context.log.info(x)
  country_of_origin_df.columns = ['country_of_origin_cleaned', 'continent_of_origin_cleaned']
  df = pd.concat([df.drop(columns=['country_of_origin']), country_of_origin_df], axis=1)
  context.log.info(f"DF after country/continent: {df.columns}")
  context.log.info("DF TRY")
  context.log.info(df[['country_of_residence_cleaned',
       'continent_of_residence_cleaned', 'country_of_origin_cleaned',
       'continent_of_origin_cleaned']])

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
  context.log.info(f"DF Columns: {df.columns})")
  context.log.info(df[['country_of_residence_cleaned',
       'continent_of_residence_cleaned', 'country_of_origin_cleaned',
       'continent_of_origin_cleaned']].head())

  df = remove_suffixes(df)
  ordered_cols = [
    "id", "ad_id", "profile_type", "name", "sex",
    "age_min", "age_max", "age_mean",
    "country_of_residence", "continent_of_residence",
    "country_of_origin", "continent_of_origin",
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
    CREATE OR REPLACE TABLE cleaned_profiles AS
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
