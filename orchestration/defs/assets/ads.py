import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource
from orchestration.extractors.sunday_rn import extract_ads_from_sunday_rn
from orchestration.extractors.special_rn import extract_ads_from_special_rn

@dg.asset(
  deps=["all_posts"]
)
def ads(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  query = """
    SELECT * FROM posts
  """
  with database.get_connection() as conn:
    posts = conn.execute(query).fetch_df()

  context.log.info(f"Number of posts loaded : {len(posts)}")

  ads = []
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
      extracted_ads = pd.DataFrame(extract_fn(post['post']), columns=["ad"])
      context.log.debug(f"Extracted ads: {extracted_ads}")
      extracted_ads['post_id'] = post['id']
      extracted_ads['post_type'] = post['type']
      ads.append(extracted_ads)
      context.log.debug(f"Number of ads extracted : {len(extracted_ads)}")
    except Exception as e:
      context.log.error(f"Error when extracting ads for post {post['id']}: {str(e)}")

    if ads:
      all_ads_df = pd.concat(ads, ignore_index=True)
    else:
      all_ads_df = pd.DataFrame(columns=["ad", "post_id"])

  context.log.info(f"Total ads : {len(all_ads_df)}")
  
  # status VARCHAR(20) DEFAULT 'NOT STARTED' CHECK (status IN ('NOT STARTED', 'PENDING', 'SUCCESS', 'FAILURE')),
  query = """
    CREATE TABLE IF NOT EXISTS ads AS 
    SELECT 
      ROW_NUMBER() OVER () AS id,
      ad,
      post_id,
      post_type,
      'NOT STARTED' AS extraction_status,
      NULL::double AS extraction_time
    FROM all_ads_df
  """
  with database.get_connection() as conn:
    conn.execute(query).fetch_df()

  return dg.MaterializeResult(
    metadata={
      "Number of posts": all_ads_df.shape[0],
      "Columns": list(all_ads_df.columns)
    }
  )



  