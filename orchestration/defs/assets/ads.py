import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource
from .posts import silver_posts
from ...core.splitting import split_ads
from ...adapters.repository import Repository

@dg.asset(
  deps=[silver_posts]
)
def ads(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
  with database.get_connection() as conn:
    repo = Repository(conn)
    posts = repo.posts_for_split()

    context.log.info(f"Nombre de posts a traiter : {len(posts)}")



    ads_extracted = []
    errors = []
    for index, post in posts.iterrows():
      context.log.debug(post)
      context.log.debug(f"Traitement du post ID = {post['id']}, Type = {post['post_type']}, Post = {post['message'][:100]}")

      try:
        extracted = split_ads(post['message'], post["post_type"])
        context.log.debug(f"Ad extrait: {len(extracted)}")

        for ad_text in extracted:
          ads_extracted.append({
            "ad": ad_text,
            "post_id": post["post_id"],
            "post_type": post["post_type"]
          })
      except Exception as e:
        errors.append({
          "post_id": post["post_id"],
          "error": str(e),
          "post_preview": post["message"][:100],
        })
        context.log.error(f"Error when extracting ads for post {post['id']}: {str(e)}")

    inserted = repo.insert_ads(pd.DataFrame(ads_extracted))
    repo.insert_ad_errors(pd.DataFrame(errors))

  context.log.info(f"{inserted} nouvelles annonces, {len(errors)} erreurs")

  return dg.MaterializeResult(metadata={
    "new_ads": dg.MetadataValue.int(inserted),
    "post_processed": dg.MetadataValue.int(len(posts)),
    "errors": dg.MetadataValue.int(len(errors))
  })
