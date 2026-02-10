from typing import List, Dict, Any
import json

LABEL_STUDIO_CONFIG = """
<View>
  <Labels name="label" toName="text">
  <Label value="AGE" background="#FFA500"/>
  <Label value="SEX" background="#800080"/>
  <Label value="HEIGHT" background="#008000"/>
  <Label value="WEIGHT" background="#008080"/>
  <Label value="COUNTRY_OF_RESIDENCE" background="#FF0000"/>
  <Label value="COUNTRY_OF_ORIGIN" background="#FF6347"/>
  <Label value="REGION" background="#FF4500"/>
  <Label value="VILLAGE" background="#FF8C00"/>
  <Label value="SECTOR_OF_ACTIVITY" background="#4682B4"/>
  <Label value="MARITAL_STATUS" background="#9370DB"/>
  <Label value="HAS_CHILDREN" background="#20B2AA"/>
  <Label value="NUMBER_OF_CHILDREN" background="#2E8B57"/>
  <Label value="RELIGION" background="#DAA520"/>
  <Label value="QUALITY" background="#FF1493"/>
  <Label value="DEFECT" background="#A9A9A9"/>
  <Label value="RELATIONSHIP_CRITERIA" background="#4169E1"/>
  </Labels>
  <Text name="text" value="$text"/>
</View>
"""

def llm_output_to_label_studio(
  ad_id: int,
  ad_text: str,
  llm_entities: List[Dict[str, Any]],
  confidence_threshold: float = 0.7
) -> Dict[str, Any]:
  """
  Convertit la sortie LLM enrichie en format Label Studio.
  
  Retourne un dictionnaire compatible avec l'API Label Studio:
  {
    "id": ad_id,
    "data": {"text": ad_text},
    "predictions": [...]  // Annotations pré-remplies par le LLM
  }
  """
  predictions = []
  
  for idx, entity in enumerate(llm_entities):
    # Filtrer les entités de faible confiance (à valider manuellement)
    if entity.get("confidence", 0) < confidence_threshold:
      continue
      
    prediction = {
      "id": f"pred-{ad_id}-{idx}",
      "from_name": "label",
      "to_name": "text",
      "type": "labels",
      "value": {
        "start": entity["start"],
        "end": entity["end"],
        "text": entity["text"],
        "labels": [entity["label"]]
      },
      "score": entity.get("confidence", 0.5)
    }
    predictions.append(prediction)
  
  return {
    "id": ad_id,
    "data": {"text": ad_text},
    "predictions": predictions  # ← Pré-annotations du LLM
  }

def export_to_label_studio_tasks(
  ads_with_entities: List[Dict[str, Any]],
  output_path: str = "label_studio_tasks.json"
):
  """Exporte une liste d'annonces au format Label Studio."""
  tasks = [
    llm_output_to_label_studio(
      ad["id"],
      ad["text"],
      ad["entities"]
    )
    for ad in ads_with_entities
  ]
  
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)
  
  print(f"✅ Exporté {len(tasks)} tâches vers {output_path}")
  print(f"💡 Importer dans Label Studio : Settings → Import → JSON")
