import dagster as dg
from dagster_duckdb import DuckDBResource
import pandas as pd
from orchestration import constants
from orchestration.helpers.hash_utils import compute_post_hash
from ...adapters.repository import Repository

@dg.asset
def bronze_posts(
  context: dg.AssetExecutionContext,
  database: DuckDBResource
) -> dg.MaterializeResult:
  with database.get_connection() as conn:
    repo = Repository(conn)
    repo.ensure_bronze_shema()
    results = repo.ingest_all_pages()
    
  total = sum(results.values())
  context.log.info(f"{total} posts bruts integres -> bronze")

  return dg.MaterializeResult(metadata={
    "bronze_posts_added": dg.MetadataValue.int(total),
    "pages": dg.MetadataValue.int(len(results))
  })

@dg.asset(
  deps=[bronze_posts]
)
def silver_posts(
  context: dg.AssetExecutionContext,
  database: DuckDBResource
) -> dg.MaterializeResult:

  with database.get_connection() as conn:
    repo = Repository(conn)
    repo.ensure_silver_schema()

    inserted = repo.promote_to_silver()
    
  context.log.info(f"{inserted} nouveaux posts -> silver")
  metadata={
    "silver_posts_added": dg.MetadataValue.int(inserted)
  }

  return dg.MaterializeResult(
    metadata=metadata
  )
