import spacy
from typing import Dict, Any, List, Optional
from .llm_service import LLMService

class HybridExtractor:
  def __init__(self, ner_model_path: str, llm_service: LLMService):
    self.ner = spacy.load(ner_model_path)
    self.llm = llm_service
  
  def extract(self, ad_text: str) -> Dict[str, Any]:
    # 1. Extraction rapide avec NER local
    doc = self.ner(ad_text)
    ner_entities = [
      {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
      for ent in doc.ents
    ]
    
    # 2. Détection des "trous" (champs manquants critiques)
    missing_critical = self._detect_missing_critical(ner_entities)
    
    if missing_critical:
      # 3. Appel LLM SEULEMENT pour les champs manquants
      llm_patch = self.llm.extract_missing_fields(ad_text, missing_critical)
      # Fusionner NER + LLM
      return self._merge_results(ner_entities, llm_patch)
    else:
      # 4. Tout extrait par NER → pas d'appel LLM
      return self._ner_to_structured(ner_entities)
  
  def _detect_missing_critical(self, entities: List[Dict]) -> List[str]:
    """Détecte les champs critiques manquants (ex: AGE, SEX)"""
    labels = {e["label"] for e in entities}
    critical = ["AGE", "SEX", "HAS_CHILDREN"]
    return [field for field in critical if field not in labels]
  