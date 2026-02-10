import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource
from .posts import posts
from orchestration.extractors.sunday_rn import extract_ads_from_sunday_rn
from orchestration.extractors.special_rn import extract_ads_from_special_rn

@dg.asset(
  deps=[posts]
)
def ads(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  query = """
    SELECT * FROM posts
  """
  with database.get_connection() as conn:
    posts = conn.execute(query).fetch_df()

  context.log.info(f"Number of posts loaded : {len(posts)}")

  ads_extracted = []
  errors = []
  for index, post in posts.iterrows():
    context.log.debug(post)
    context.log.debug(f"Processing of post {index}: ID = {post['id']}, Type = {post['type']}, Post = {post['post'][:100]}")

    extract_fn = (
      extract_ads_from_sunday_rn
      if post['type'] == 'Dimanche'
      else extract_ads_from_special_rn
    )
    context.log.debug(f"Extraction function selected : {extract_fn.__name__}")

    try:
      extracted = extract_fn(post['post'])
      context.log.debug(len(extracted))
      if extracted:
        for ad_text in extracted:
          ads_extracted.append({
            "ad": ad_text,
            "post_id": post["id"],
            "post_type": post["type"]
          })
    except Exception as e:
      errors.append({
        "post_id": post["id"],
        "error": str(e),
        "post_preview": post["post"][:100],
      })
      context.log.error(f"Error when extracting ads for post {post['id']}: {str(e)}")

  if ads_extracted:
    ads_df = pd.DataFrame(ads_extracted)
    context.log.info(f"Extraction success: {len(ads_df)} ads from {len(posts)} posts")
  else:
    ads_df = pd.DataFrame(columns=["ad", "post_id", "post_type"])
    context.log.warning("No ads extracted")
  
  # status VARCHAR(20) DEFAULT 'NOT STARTED' CHECK (status IN ('NOT STARTED', 'PENDING', 'SUCCESS', 'FAILURE')),
  with database.get_connection() as conn:
    conn.execute("""
      CREATE OR REPLACE TABLE ads (
        id INTEGER PRIMARY KEY,
        ad VARCHAR NOT NULL,
        post_id VARCHAR NOT NULL,
        post_type VARCHAR NOT NULL,
        extraction_status VARCHAR DEFAULT 'NOT STARTED' 
                CHECK (extraction_status IN ('NOT STARTED', 'PENDING', 'SUCCESS', 'FAILURE')),
        extraction_time DOUBLE
      )          
    """)
    if not ads_df.empty:
      conn.execute("""
        INSERT INTO ads(id, ad, post_id, post_type, extraction_status, extraction_time)
        SELECT
          ROW_NUMBER() OVER () AS id,
          ad,
          post_id,
          post_type,
          'NOT STARTED' AS extraction_status,
          NULL::double AS extraction_time
        FROM ads_df
      """)

    # Ajouter une table d'audit des erreurs
    if errors:
      errors_df = pd.DataFrame(errors)
      conn.execute("""
        CREATE TABLE IF NOT EXISTS ads_extraction_errors (
          post_id INTEGER,
          error VARCHAR,
          post_preview VARCHAR,
          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      """)
      conn.execute("INSERT INTO ads_extraction_errors(post_id, error, post_preview) SELECT * FROM errors_df")

    total_ads = conn.execute("SELECT COUNT(*) FROM ads").fetchone()[0]
    posts_with_ads = conn.execute("""
      SELECT COUNT(DISTINCT post_id) FROM ads
    """).fetchone()[0]
    

    metadata = {
      "total_ads": dg.MetadataValue.int(total_ads),
      "posts_processed": dg.MetadataValue.int(len(posts)),
      "posts_with_ads": dg.MetadataValue.int(posts_with_ads),
      "extraction_success_rate": dg.MetadataValue.float(
        (posts_with_ads / len(posts)) * 100 if len(posts) > 0 else 0.0
      ),
      "errors_count": dg.MetadataValue.int(len(errors))
    }

  return dg.MaterializeResult(metadata=metadata)
