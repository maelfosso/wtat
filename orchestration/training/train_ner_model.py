import spacy
from spacy.training import Example
import json

def label_studio_to_spacy(json_path: str):
  """Convertit export Label Studio → format spaCy training"""
  with open(json_path) as f:
    data = json.load(f)
  
  spacy_data = []
  for task in data:
    text = task["data"]["text"]
    entities = []
    
    for annotation in task.get("annotations", []):
      for result in annotation.get("result", []):
        if result["type"] == "labels":
          entities.append((
            result["value"]["start"],
            result["value"]["end"],
            result["value"]["labels"][0]  # Premier label
          ))
    
    spacy_data.append((text, {"entities": entities}))
  
  return spacy_data

# Entraînement
nlp = spacy.blank("fr")
ner = nlp.add_pipe("ner")

# Ajouter tous les labels
for label in ["AGE", "SEX", "HEIGHT", "COUNTRY_OF_RESIDENCE", ...]:
  ner.add_label(label)

# Entraîner
train_data = label_studio_to_spacy("export_label_studio.json")
examples = [Example.from_dict(nlp.make_doc(text), annot) for text, annot in train_data]

nlp.initialize()
for _ in range(30):  # 30 itérations
  losses = {}
  nlp.update(examples, losses=losses)
  print(f"Loss: {losses}")

nlp.to_disk("models/matrimonial_ner")
