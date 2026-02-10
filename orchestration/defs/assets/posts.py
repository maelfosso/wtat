import dagster as dg
from dagster_duckdb import DuckDBResource
import pandas as pd
from orchestration import constants
from orchestration.helpers.hash_utils import compute_post_hash

monthly_partitions = dg.WeeklyPartitionsDefinition(
  start_date="01-12-2021",
  end_date="01-01-2022",
  day_of_week=1,
  fmt="%d-%m-%Y"
)

columns_mapping = {
  "Date": "date",
  "Post": "post"
}
@dg.asset(partitions_def=monthly_partitions)
def special_posts(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  posts = pd.read_excel(
    constants.DATA_2021_FILE_PATH,
    sheet_name="Recherche NDolo",
    parse_dates=['Date'],
    date_format='%d/%m/%Y'
  )
  posts.rename(columns=columns_mapping, inplace=True)
  posts['date'] = pd.to_datetime(posts['date'])
  posts['type'] = 'Special'
  posts['hash'] = posts.apply(
    lambda p: compute_post_hash(p['date'], p['post']),
    axis=1
  )

  start, end = context.partition_time_window
  start_naive = start.replace(tzinfo=None)
  end_naive = end.replace(tzinfo=None)

  filtered_posts = posts[
    (posts['date'] >= start_naive) &
    (posts['date'] < end_naive)
  ].copy()
  filtered_posts["partition_key"] = context.partition_key

  with database.get_connection() as conn:
    conn.execute("""
      CREATE TABLE IF NOT EXISTS special_posts_staging (
        date TIMESTAMP,
        post VARCHAR,
        type VARCHAR,
        hash VARCHAR,
        partition_key VARCHAR           
      )
    """)
    conn.execute("""
      DELETE FROM special_posts_staging WHERE partition_key = ?            
    """, [context.partition_key])
    if not filtered_posts.empty:
      conn.execute("INSERT INTO special_posts_staging SELECT * FROM filtered_posts")

  context.log.info(f"Partition {context.partition_key}: {len(filtered_posts)} special posts")
  return dg.MaterializeResult(metadata={
    "num_posts": dg.MetadataValue.int(len(filtered_posts)),
    "partition_key": dg.MetadataValue.text(context.partition_key)
  })

@dg.asset(partitions_def=monthly_partitions)
def sunday_posts(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  posts = pd.read_excel(
    constants.DATA_2021_FILE_PATH,
    sheet_name="RN Dimanche"
  )
  posts.rename(columns=columns_mapping, inplace=True)
  posts['date'] = pd.to_datetime(posts['date'])
  posts['type'] = 'Dimanche'
  posts['hash'] = posts.apply(
    lambda p: compute_post_hash(p['date'], p['post']),
    axis=1
  )

  start, end = context.partition_time_window
  start_naive = start.replace(tzinfo=None)
  end_naive = end.replace(tzinfo=None)

  filtered_posts = posts[
    (posts['date'] >= start_naive) &
    (posts['date'] < end_naive)
  ].copy()
  filtered_posts['partition_key'] = context.partition_key

  with database.get_connection() as conn:
    conn.execute("""
      CREATE TABLE IF NOT EXISTS sunday_posts_staging (
        date TIMESTAMP,
        post VARCHAR,
        type VARCHAR,
        hash VARCHAR,
        partition_key VARCHAR           
      )
    """)
    conn.execute("""
      DELETE FROM sunday_posts_staging WHERE partition_key = ?             
    """, [context.partition_key])
    if not filtered_posts.empty:
      conn.execute("INSERT INTO sunday_posts_staging SELECT * FROM filtered_posts")

  context.log.info(f"Partition {context.partition_key}: {len(filtered_posts)} sunday posts")
  return dg.MaterializeResult(metadata={
    "num_posts": dg.MetadataValue.int(len(filtered_posts)),
    "partition_key": dg.MetadataValue.text(context.partition_key)
  })

  return filtered_posts

@dg.asset(
  deps=[sunday_posts, special_posts]
)
def posts(
  context: dg.AssetExecutionContext,
  database: DuckDBResource
) -> dg.MaterializeResult:

  with database.get_connection() as conn:
    conn.execute("""
      CREATE OR REPLACE TABLE posts AS
      SELECT date, post, type, hash AS id, partition_key
      FROM special_posts_staging
      
      UNION ALL
                 
      SELECT date, post, type, hash AS id, partition_key
      FROM sunday_posts_staging
                 
      ORDER BY date DESC
    """)

    total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    by_type = conn.execute("""
      SELECT type, COUNT(*) AS count
      FROM posts
      GROUP BY type
    """).fetchall()
    by_partition = conn.execute("""
      SELECT partition_key, COUNT(*) AS count
      FROM posts
      GROUP BY partition_key
      ORDER BY partition_key
    """).fetchall()

  context.log.info(f"Successfully inserted {total} posts")

  metadata={
    "#Posts": total,
    "partitions included": dg.MetadataValue.text(
      ", ".join([p[0] for p in by_partition])
    ),
    "#Partitions": dg.MetadataValue.int(len(by_partition))
  }
  for type_item, count in by_type:
    metadata[f"posts_{type_item.lower()}"] = dg.MetadataValue.int(count)

  return dg.MaterializeResult(
    metadata=metadata
  )
