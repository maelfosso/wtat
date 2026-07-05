# import dagster as dg
# from dagster_duckdb import DuckDBResource
# import json
# from pathlib import Path
# from orchestration.label_studio.converter import export_to_label_studio_tasks, LABEL_STUDIO_CONFIG

# @dg.asset(
#   deps=["profiles"],
#   config_schema={
#     "output_dir": dg.Field(str, default_value="data/label-studio"),
#     "min_confidence": dg.Field(float, default_value=0.6)
#   }
# )
# def label_studio_tasks(
#   context: dg.AssetExecutionContext,
#   database: DuckDBResource
# ) -> dg.MaterializeResult:
#   """
#   Génère des tâches Label Studio pré-annotées à partir des extractions LLM.
#   Les annotations du LLM servent de suggestions à valider/corriger par un humain.
#   """
#   output_dir = Path(context.op_config["output_dir"])
#   output_dir.mkdir(parents=True, exist_ok=True)
  
#   # Charger les annonces avec leurs entités LLM
#   with database.get_connection() as conn:
#     ads_with_entities = conn.execute("""
#       SELECT 
#         a.id,
#         a.ad AS text,
#         p.entities_seeker AS seeker,
#         p.entities_sought AS sought                                    
#       FROM ads a
#       JOIN raw_profiles p ON a.id = p.ad_id
#       WHERE p.extraction_error IS NULL
#         AND p.entities_seeker IS NOT NULL
#         AND p.entities_sought IS NOT NULL                             
#     """).fetch_df()
  
#   # Convertir chaque annonce
#   tasks = []
#   for _, row in ads_with_entities.iterrows():
#     try:
#       seeker = json.loads(row["seeker"])
#       sought = json.loads(row["sought"])

#       tasks.append({
#         "id": row["id"],
#         "text": row["text"],
#         "entities": {
#           "seeker": seeker,
#           "sought": sought
#         }
#       })
#     except Exception as e:
#       context.log.warning(f"❌ Erreur parsing entités AD {row['id']}: {e}")
  
#   # Exporter vers Label Studio
#   output_path = output_dir / "tasks.json"
#   export_to_label_studio_tasks(tasks, str(output_path))
  
#   # Sauvegarder aussi la config Label Studio
#   config_path = output_dir / "label_config.xml"
#   with open(config_path, "w") as f:
#     f.write(LABEL_STUDIO_CONFIG)
  
#   return dg.MaterializeResult(
#     metadata={
#       "tasks_exported": len(tasks),
#       "output_path": str(output_path),
#       "min_confidence_used": context.op_config["min_confidence"]
#     }
#   )

# @dg.asset(
#   deps=["label_studio_tasks"],
#   config_schema={
#     "label_studio_url": dg.Field(str, default_value="http://localhost:8080"),
#     "project_id": dg.Field(int, description="ID du projet Label Studio", default_value=1)
#   }
# )
# def import_to_label_studio(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
#   """
#   Importe automatiquement les tâches dans Label Studio via son API.
#   Nécessite LABEL_STUDIO_API_KEY dans les variables d'environnement.
#   """
#   import requests
#   import os
  
#   api_key = os.getenv("LABEL_STUDIO_API_KEY")
#   if not api_key:
#     raise ValueError("LABEL_STUDIO_API_KEY non défini dans l'environnement")
  
#   context.log.info(f"LABEL_STUDIO_API_KEY: {api_key}")
  
#   project_id = context.op_config["project_id"]
#   tasks_path = Path("data/label-studio/tasks.json")
  
#   with open(tasks_path, "r") as f:
#     tasks = json.load(f)
  
#   # Appel API Label Studio
#   response = requests.post(
#     f"{context.op_config['label_studio_url']}/api/projects/{project_id}/import",
#     headers={"Authorization": f"Token {api_key}"},
#     json=tasks
#   )
  
#   if response.status_code != 201:
#     raise Exception(f"Échec import Label Studio: {response.text}")
  
#   imported_count = len(response.json().get("task_ids", []))
  
#   return dg.MaterializeResult(
#     metadata={
#       "tasks_imported": imported_count,
#       "label_studio_project": project_id,
#       "api_status": response.status_code
#     }
#   )
