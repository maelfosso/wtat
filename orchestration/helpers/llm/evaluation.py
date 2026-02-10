from typing import Dict, Any, List, Tuple
import re

def evaluate_llm_extraction(
  announcement_text: str,
  extracted_json: Dict[str, Any],
  profile_type: str = "advertiser"
) -> Dict[str, Any]:
  """
  Évalue objectivement la qualité de l'extraction LLM.
  
  Retourne:
    {
      "error_score": float (0.0 = parfait, 1.0 = échec total),
      "field_scores": Dict[str, float],  # Score par champ (0=erreur, 1=correct)
      "critical_errors": List[str],    # Erreurs bloquantes
      "suggestions": List[str],      # Corrections suggérées
      "missing_critical_info": List[str] # Infos explicites non extraites
    }
  """
  weights = {
    # Champs critiques (échec = données inutilisables)
    "SEX": 15, "AGE": 15, "HAS_CHILDREN": 20, "NUMBER_OF_CHILDREN": 20,
    "PRIMARY_COUNTRY_OF_RESIDENCE": 15, "COUNTRY_OF_ORIGIN": 10,
    "RELATIONSHIP": 25,
    # Champs contextuels
    "HEIGHT": 5, "WEIGHT": 5, "MARITAL_STATUS": 8, "RELIGION": 8,
    "QUALITIES": 5, "VALUES": 4, "DEFECTS": 4, "INTERESTS": 3,
    "PHYSICAL_APPEARANCE": 4, "ECONOMIC_SITUATION": 4,
    "EDUCATION_LEVEL": 5, "ILLNESS": 2
  }
  
  field_scores = {}
  critical_errors = []
  suggestions = []
  missing_critical_info = []
  total_weight = sum(weights.values())
  weighted_errors = 0.0
  
  text_lower = announcement_text.lower()
  
  # === VALIDATION PAR CHAMP ===
  
  # 1. SEX (critique)
  sex = extracted_json.get("SEX")
  sex_expected = None
  if any(kw in text_lower for kw in ["femme", "jeune femme", "camerounaise", "maman"]):
    sex_expected = "Femme"
  elif any(kw in text_lower for kw in ["homme", "monsieur", "camerounais", "papa"]):
    sex_expected = "Homme"
  
  if sex_expected and sex == sex_expected:
    field_scores["SEX"] = 1.0
  else:
    field_scores["SEX"] = 0.0
    weighted_errors += weights["SEX"]
    if sex_expected:
      missing_critical_info.append(f"SEX: attendu '{sex_expected}' mais obtenu '{sex}'")
  
  # 2. AGE (critique)
  age = extracted_json.get("AGE")
  age_match = re.search(r'(\d+)\s*(?:ans?|years?)', text_lower)
  if age_match and age and age_match.group(1) in str(age):
    field_scores["AGE"] = 1.0
  else:
    field_scores["AGE"] = 0.0
    weighted_errors += weights["AGE"]
    if age_match:
      missing_critical_info.append(f"AGE: chiffre '{age_match.group(1)}' non extrait correctement")
  
  # 3. HAS_CHILDREN + NUMBER_OF_CHILDREN (critique)
  has_children_expected = None
  num_children_expected = None
  
  if "sans enfant" in text_lower or "childless" in text_lower:
    has_children_expected = "Non"
    num_children_expected = "0"
  elif any(kw in text_lower for kw in ["enfant", "bambin", "gamin", "rejeton", "maman", "papa"]):
    has_children_expected = "Oui"
    # Extraire nombre
    num_match = re.search(r'(\d+)\s*(?:enfant|bambin|gamin|rejeton)', text_lower)
    if num_match:
      num_children_expected = num_match.group(1)
    else:
      # Recherche mots numéraux
      num_words = {"un": "1", "une": "1", "deux": "2", "trois": "3", "quatre": "4", "cinq": "5"}
      for word, num in num_words.items():
        if word in text_lower:
          num_children_expected = num
          break
  
  has_children = extracted_json.get("HAS_CHILDREN")
  num_children = extracted_json.get("NUMBER_OF_CHILDREN")
  
  # Normaliser "00" → "0"
  if num_children == "00":
    num_children = "0"
    suggestions.append("NUMBER_OF_CHILDREN: '00' converti en '0'")
  
  if has_children_expected and has_children == has_children_expected:
    field_scores["HAS_CHILDREN"] = 1.0
  else:
    field_scores["HAS_CHILDREN"] = 0.0
    weighted_errors += weights["HAS_CHILDREN"]
    if has_children_expected:
      missing_critical_info.append(f"HAS_CHILDREN: attendu '{has_children_expected}' mais obtenu '{has_children}'")
  
  if num_children_expected and num_children == num_children_expected:
    field_scores["NUMBER_OF_CHILDREN"] = 1.0
  elif num_children_expected and num_children is None:
    field_scores["NUMBER_OF_CHILDREN"] = 0.0
    weighted_errors += weights["NUMBER_OF_CHILDREN"]
    missing_critical_info.append(f"NUMBER_OF_CHILDREN: chiffre '{num_children_expected}' non extrait")
  else:
    field_scores["NUMBER_OF_CHILDREN"] = 0.5  # Partiellement correct
    weighted_errors += weights["NUMBER_OF_CHILDREN"] * 0.5
  
  # 4. PAYS DE RÉSIDENCE (critique)
  residence = extracted_json.get("PRIMARY_COUNTRY_OF_RESIDENCE")
  # Pays attendus dans les annonces types
  expected_countries = ["france", "allemagne", "usa", "états-unis", "canada", "cameroun"]
  if residence and any(country in text_lower for country in expected_countries if country in residence.lower()):
    field_scores["PRIMARY_COUNTRY_OF_RESIDENCE"] = 1.0
  else:
    field_scores["PRIMARY_COUNTRY_OF_RESIDENCE"] = 0.0
    weighted_errors += weights["PRIMARY_COUNTRY_OF_RESIDENCE"]
    if any(country in text_lower for country in expected_countries):
      missing_critical_info.append(f"PRIMARY_COUNTRY_OF_RESIDENCE: pays non extrait correctement")
  
  # 5. RELATIONSHIP (critique - vérifier couverture minimale)
  relationship = extracted_json.get("RELATIONSHIP", [])
  has_age = any(re.search(r'\d+\s*-\s*\d+\s*ans?', str(r).lower()) for r in relationship)
  has_location = any(loc in str(relationship).lower() for loc in ["europe", "afrique", "canada", "usa", "france", "allemagne"])
  has_parental = any(kw in str(relationship).lower() for kw in ["enfant", "papa", "maman", "parent"])
  
  if relationship and (has_age or has_location or has_parental):
    field_scores["RELATIONSHIP"] = 1.0 if len(relationship) >= 2 else 0.7
  else:
    field_scores["RELATIONSHIP"] = 0.0
    weighted_errors += weights["RELATIONSHIP"]
    missing_critical_info.append("RELATIONSHIP: critères de recherche non extraits")
  
  # 6. DÉTECTION D'HALLUCINATIONS (pénalité lourde)
  # Ex: religion mentionnée alors qu'absente du texte
  religion = extracted_json.get("RELIGION")
  if religion and religion.lower() not in text_lower and "religion" not in text_lower:
    critical_errors.append(f"Hallucination RELIGION: '{religion}' non présent dans l'annonce")
    weighted_errors += 30  # Pénalité lourde
  
  # === CALCUL SCORE FINAL ===
  error_score = min(weighted_errors / total_weight, 1.0)
  
  return {
    "error_score": round(error_score, 3),
    "field_scores": field_scores,
    "critical_errors": critical_errors,
    "suggestions": suggestions,
    "missing_critical_info": missing_critical_info,
    "is_acceptable": error_score <= 0.3  # Seuil configurable
  }
