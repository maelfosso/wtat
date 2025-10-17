import dagster as dg
from dagster_duckdb import DuckDBResource
import pandas as pd
from orchestration import constants
from orchestration.helpers.hash_utils import compute_post_hash

columns_mapping = {
  "Date": "date",
  "Post": "post"
}
@dg.asset
def special_posts(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  posts = pd.read_excel(constants.DATA_2021_FILE_PATH, sheet_name="Recherche NDolo")
  posts.rename(columns=columns_mapping, inplace=True)
  posts['type'] = 'Special'
  posts['hash'] = posts.apply(lambda p: compute_post_hash(p['date'], p['post']), axis=1)

  return posts

@dg.asset
def sunday_posts(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  posts = pd.read_excel(constants.DATA_2021_FILE_PATH, sheet_name="RN Dimanche")
  posts.rename(columns=columns_mapping, inplace=True)
  posts['type'] = 'Dimanche'
  posts['hash'] = posts.apply(lambda p: compute_post_hash(p['date'], p['post']), axis=1)

  return posts

@dg.asset(
  deps=[sunday_posts, special_posts]
)
def all_posts(
  context: dg.AssetExecutionContext,
  special_posts: pd.DataFrame,
  sunday_posts: pd.DataFrame,
  database: DuckDBResource) -> dg.MaterializeResult:

  all_posts_df = pd.concat([special_posts, sunday_posts], ignore_index=True)
  
  context.log.info(f"sunday_posts: \n{sunday_posts}")
  context.log.info(f"special_posts: \n{special_posts}")
  context.log.info(f"All posts: \n{all_posts_df}")

  with database.get_connection() as conn:
    conn.execute("""
      CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        date DATE,
        hash VARCHAR UNIQUE,
        post TEXT,
        type VARCHAR           
      )
    """)

    for i, post in all_posts_df.iterrows():
      conn.execute(
        "INSERT OR IGNORE INTO posts (id, date, hash, post, type) VALUES (?, ?, ?, ?, ?)",
        (i + 1, post['date'], post['hash'], post['post'], post['type'])
      )

    count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    context.log.info(f"Successfully inserted {count} posts")

  return dg.MaterializeResult(
    metadata={
      "Sunday posts": sunday_posts.shape[0],
      "Special posts": special_posts.shape[0],
      "Total posts": all_posts_df.shape[0],
      "Posts in DB": count
    }
  )