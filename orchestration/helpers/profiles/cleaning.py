import re
import pandas as pd
import numpy as np
import unidecode


# =====================================================
# 1️⃣ ÂGE
# =====================================================

def parse_age(age_str):
  """Convertit une chaîne d'âge en (age_min, age_max, age_median)."""
  if not age_str or not isinstance(age_str, str):
    return (np.nan, np.nan, np.nan)
  
  age_str = age_str.strip().lower()

  # "plus de 50 ans" (forme non gérée avant)
  if re.match(r"plus de\s*\d{1,2}", age_str):
    a = int(re.search(r"\d{1,2}", age_str).group())
    return (a, 99, a + (99 - a) / 2)

  # "moins de X ans"
  if re.match(r"moins de\s*\d{1,2}", age_str):
    a = int(re.search(r"\d{1,2}", age_str).group())
    return (0, a, a / 2)

  # 1️⃣ Forme "X ans" (un seul âge)
  single_age = re.match(r"^(\d{1,2})\s*ans?$", age_str)
  if single_age:
    age = int(single_age.group(1))
    return (age, age, age)

  # 2️⃣ Forme "X-Y ans" ou "X à Y ans"
  range_age = re.match(r"^(\d{1,2})\s*(?:-|à|–)\s*(\d{1,2})", age_str)
  if range_age:
    a1, a2 = int(range_age.group(1)), int(range_age.group(2))
    return (a1, a2, (a1 + a2) / 2)

  # 3️⃣ Forme "max X ans" ou "X ans max"
  max_age = re.match(r"^(?:max\s*)?(\d{1,2})\s*ans\s*(?:max)?$", age_str)
  if max_age:
    a = int(max_age.group(1))
    return (0, a, a / 2)

  # 4️⃣ Forme "min X ans"
  min_age = re.match(r"^(?:min\s*)?(\d{1,2})\s*ans$", age_str)
  if min_age and "min" in age_str:
    a = int(min_age.group(1))
    return (a, 99, a + (99 - a) / 2)

  # 5️⃣ Forme "moins de X ans"
  less_age = re.match(r"moins de\s*(\d{1,2})", age_str)
  if less_age:
    a = int(less_age.group(1))
    return (0, a, a / 2)

  # 6️⃣ Forme "plus de X ans" / "X ans et plus" / "X ans ou plus"
  more_age = re.match(r"(\d{1,2})\s*ans?\s*(et|ou)?\s*plus", age_str)
  if more_age:
    a = int(more_age.group(1))
    return (a, 99, a + (99 - a) / 2)

  # 7️⃣ Autres formes "20-35" sans "ans"
  range_simple = re.match(r"(\d{1,2})\s*[-à]\s*(\d{1,2})", age_str)
  if range_simple:
    a1, a2 = int(range_simple.group(1)), int(range_simple.group(2))
    return (a1, a2, (a1 + a2) / 2)

  return (np.nan, np.nan, np.nan)



# =====================================================
# 2️⃣ SEXE
# =====================================================

def normalize_sex(value: str) -> str:
  if not value:
    return None

  v = value.strip().lower()

  homme_terms = ["homme", "masculin", "m", "h", "mâle"]
  femme_terms = ["femme", "feminin", "féminin", "fille", "f"]

  if v in homme_terms:
    return "Homme"
  if v in femme_terms:
    return "Femme"

  return None


# =====================================================
# 3️⃣ PAYS & CONTINENT
# =====================================================

country_map = {
  "france": "France",
  "idf": "France",
  "ile-de-france": "France",
  "union europeenne": "Union Européenne",
  "ue": "Union Européenne",
  "eu": "Union Européenne",
  "europe": "Union Européenne",
  "belgique": "Belgique",
  "luxembourg": "Luxembourg",
  "suisse": "Suisse",
  "allemagne": "Allemagne",
  "germany": "Allemagne",
  "uk": "Angleterre",
  "england": "Angleterre",
  "angleterre": "Angleterre",
  "espagne": "Espagne",
  "italie": "Italie",
  "etats-unis": "États-Unis",
  "usa": "États-Unis",
  "amerique du nord": "États-Unis",
  "canada": "Canada",
  "cameroun": "Cameroun",
  "cameroon": "Cameroun",
  "gabon": "Gabon",
  "senegal": "Sénégal",
  "republique centrafricaine": "République Centrafricaine",
  "central african republic": "République Centrafricaine",
  "asie": "Asie",
  "afrique": "Afrique",
  "afrique de l’ouest": "Afrique",
  "amerique": "Amérique",
  "schengen": "Union Européenne",
  "espace schengen": "Union Européenne"
}

# 🔹 Dictionnaire de correspondance pays → continent
continent_map = {
  "France": "Europe",
  "Belgique": "Europe",
  "Luxembourg": "Europe",
  "Suisse": "Europe",
  "Allemagne": "Europe",
  "Union Européenne": "Europe",
  "Angleterre": "Europe",
  "Espagne": "Europe",
  "Italie": "Europe",
  "Canada": "Amérique du Nord",
  "États-Unis": "Amérique du Nord",
  "Cameroun": "Afrique",
  "Gabon": "Afrique",
  "Sénégal": "Afrique",
  "République Centrafricaine": "Afrique",
  "Afrique": "Afrique",
  "Asie": "Asie",
  "Amérique": "Amérique du Nord"
}

def normalize_and_map_country(value):
  """
  Nettoie, normalise et mappe un ou plusieurs pays à leurs continents.
  Retourne une liste de dicts : [{"country": ..., "continent": ...}]
  """
  # Si c'est un array, une Series ou une liste, on transforme en string
  if isinstance(value, (list, np.ndarray, pd.Series)):
    value = ", ".join(str(v) for v in value if pd.notna(v))

  # Vérifier NaN ou chaine vide
  if pd.isna(value) or not isinstance(value, str) or value.strip() == "":
    return []

  text = unidecode.unidecode(value.strip().lower())

  parts = [p.strip() for p in text.split(",") if p.strip()]

  result = []
  for p in parts:
    normalized_country = country_map.get(p, p.capitalize())
    continent = continent_map.get(normalized_country, "Autre")
    result.append({
      "country": normalized_country,
      "continent": continent
    })
  return result


# =====================================================
# 4️⃣ RÉGION & VILLAGE
# =====================================================
region_map = {
  # Ouest
  "ouest": "Ouest",
  "ouest cameroun": "Ouest",
  "ouest-cameroun": "Ouest",
  "ouest (ndé)": "Ouest",
  "l'ouest": "Ouest",
  "l ouest": "Ouest",
  "l'ouest du cameroun": "Ouest",
  "ouest du cameroun": "Ouest",
  "o": "Ouest",
  "ndé": "Ouest",
  "nde": "Ouest",
  "bafoussam": "Ouest",
  "dschang": "Ouest",
  "menoua": "Ouest",
  "koung-khi": "Ouest",
  "bamboutos": "Ouest",
  "bangangte": "Ouest",
  "bagangté": "Ouest",
  "bandjoun": "Ouest",
  "balatchi": "Ouest",
  "mbouda": "Ouest",
  "bamendjou": "Ouest",
  "bayangam": "Ouest",
  "mbamboutos": "Ouest",
  "haut-nkam": "Ouest",
  "haut nkam": "Ouest",
  "hauts plateaux": "Ouest",
  "mboa": "Centre",  # village de Mbam-Mfoundi
  "eton": "Centre",
  "bassa'a": "Littoral",
  "bassa": "Littoral",
  "nko": "Ouest",

  # Centre
  "centre": "Centre",
  "yaoundé": "Centre",
  "mbam": "Centre",
  "yde": "Centre",  # abréviation pour Yaoundé
  "okola": "Centre",

  # Littoral
  "littoral": "Littoral",
  "douala": "Littoral",

  # Nord
  "nord": "Nord",
  "nord cameroun": "Nord",
  "adamaoua": "Adamaoua",  # Adamawa
  "est": "Est",
  "est du cameroun": "Est",

  # Sud
  "sud": "Sud",
  "sud-ouest": "Sud-Ouest",
  "sud ouest": "Sud-Ouest",

  # Nord-Ouest
  "nord-ouest": "Nord-Ouest",
  "north-west": "Nord-Ouest",

  # Sud-Ouest
  "south-west": "Sud-Ouest",

  # Autres ou hors Cameroun
  "île-de-france": None,
  "rennes": None,
  "région parisienne": None,
  "west": "Ouest",  # parfois utilisé par anglophones
  "kho": "Ouest",
  "dla": "Ouest",
  "resse 14": None,
  "a": None,
  "s": None,
  "r": None,
  "cameroon": None,  # général
}

# Supposons profiles['region_of_origin'] et profiles['village_of_origin'] existent
def normalize_region(value):
  if pd.isna(value):
    return None
  key = str(value).strip().lower()
  return region_map.get(key, None)  # retourne None si valeur inconnue

# Si la région est manquante mais le village est connu, utiliser le mapping village -> région
def fill_region_from_village(row):
  if row['region_normalized'] is None and pd.notna(row['village_of_origin']):
    key = str(row['village_of_origin']).strip().lower()
    return region_map.get(key, None)
  return row['region_normalized']

# Nettoyer village_of_origin si c'est en réalité une région ou artefact
def clean_village(value):
  if pd.isna(value):
    return None
  key = str(value).strip().lower()
  if key in region_map:
    # Si la clé correspond à une région, on ne garde pas dans village
    return None
  return value

# profiles['region_normalized'] = profiles.apply(fill_region_from_village, axis=1)
# profiles['village_cleaned'] = profiles['village_of_origin'].apply(clean_village)


# =====================================================
# 5️⃣ SECTEUR / PROFESSION
# =====================================================

sector_map = {
  # Études / Éducation
  "Étudiant": "Études / Éducation",
  "Étudiante": "Études / Éducation",
  "Enseignant": "Études / Éducation",
  "Professeur": "Études / Éducation",
  
  # Entrepreneuriat / Affaires
  "Entrepreneur": "Entrepreneuriat / Affaires",
  "Commerce": "Entrepreneuriat / Affaires",
  "Business": "Entrepreneuriat / Affaires",
  
  # Ingénierie / Technique / IT
  "Ingénieur": "Ingénierie / Technique / IT",
  "Informaticien": "Ingénierie / Technique / IT",
  "Technicien": "Ingénierie / Technique / IT",
  
  # Médecine / Santé
  "Médecin": "Médecine / Santé",
  "Vétérinaire": "Médecine / Santé",
  "Chirurgie": "Médecine / Santé",
  "Infirmier": "Médecine / Santé",
  
  # Marketing / Communication / Vente
  "Marketing": "Marketing / Communication / Vente",
  "Commercial": "Marketing / Communication / Vente",
  "Communication": "Marketing / Communication / Vente",
  
  # Art / Culture / Evénementiel
  "Organisatrice événementielle": "Art / Culture / Evénementiel",
  "Artiste": "Art / Culture / Evénementiel",
  "Musicien": "Art / Culture / Evénementiel",
  
  # Autres ou non renseigné
  None: "Non renseigné"
}

def normalize_sector(value):
  """Regroupe les secteurs en catégories standards"""
  return sector_map.get(value, "Autres")

# profiles['sector_grouped'] = profiles['sector_of_activity'].map(lambda x: sector_map.get(x, "Autres"))


# =====================================================
# 6️⃣ STATUT MATRIMONIAL
# =====================================================

marital_map = {
  # Célibataires
  "Célibataire": "Célibataire",
  "célibataire": "Célibataire",
  "Celibataire": "Célibataire",
  "prêt pour le mariage": "Célibataire",
  "seul": "Célibataire",
  
  # Divorcé(e) / Séparé(e)
  "Divorcée": "Divorcé(e)",
  "Divorcé": "Divorcé(e)",
  "Séparée": "Divorcé(e)",
  "Non divorcé": "Célibataire",  # à vérifier selon le contexte
  "Célibataire ou divorcé": "Divorcé(e)",
  
  # Marié(e)
  "Mariée": "Marié(e)",
  
  # Veuf / Veuve
  "Veuve": "Veuf / Veuve",
  
  # Inconnu / Indétectable
  # "Indétectable": "Inconnu"
}

def normalize_marital_status(value):
  return marital_map.get(value, "Autres")

# profiles['marital_status_normalized'] = profiles['marital_status'].map(lambda x: marital_map.get(x, "Autre"))

# =====================================================
# 7️⃣ ENFANTS
# =====================================================

def clean_number_of_children(val):
  if val is None:
    return 0
  val_str = str(val).lower().strip()
  
  # Cas explicites
  if val_str in ["sans enfant", "0"]:
    return 0
  if val_str in ["1 enfant", "1", "0-1 enfant"]:
    return 1
  if val_str in ["2"]:
    return 2
  if val_str in ["3 enfants", "3"]:
    return 3
  if val_str in ["4"]:
    return 4
  
  # Extraire nombre si présent dans le texte
  match = re.search(r"\d+", val_str)
  if match:
    return int(match.group(0))
  
  # Si rien trouvé, considérer 0
  return 0

# profiles['number_of_children_cleaned'] = profiles['number_of_children'].apply(clean_number_of_children)
# profiles['has_children_cleaned'] = profiles['number_of_children_cleaned'].apply(lambda x: x > 0)

# =====================================================
# 8️⃣ SANTÉ
# =====================================================

illness_keywords = [
    "indétectable", "vih", "diabète", "hypertension", "cancer", 
    "asthme", "hiv", "hepatite", "malade", "condition médicale"
]

# Fonction pour détecter si l'annonce mentionne une maladie
def detect_illness(text):
    if text is None:
        return False
    text_lower = str(text).lower()
    return any(keyword in text_lower for keyword in illness_keywords)

# Créer la feature has_illness
# profiles['has_illness'] = profiles['illness'].apply(detect_illness) | \
#                           profiles['marital_status'].apply(detect_illness)

def normalize_illness(value):
  if value is None or pd.isna(value):
    return "Aucune"
  
  # Nettoyage de base
  value = str(value).strip()
  value = unidecode.unidecode(value.lower())
  value = re.sub(r"[\[\]']", "", value)
  
  # Cas vides ou neutres
  if value in ["", "none", "aucune", "aucun", "[]"]:
    return "Aucune"
  
  # Cas spécifiques
  if "handicap" in value:
    return "Handicap"
  
  if "sero" in value or "vih" in value or "charge virale" in value:
    return "VIH / Séropositif"
  
  # Par défaut
  return "Autre"

# profiles['illness_cleaned'] = profiles['illness'].apply(normalize_illness)


# =====================================================
# 9️⃣ QUALITÉS / VALEURS / DÉFAUTS / INTÉRÊTS
# =====================================================

def list_to_string(value):
  """Convertit une liste ou texte multivalué en chaîne propre"""
  if value is None:
    return None
  if isinstance(value, (float, np.floating)) and pd.isna(value):
    return None

  # if isinstance(value, list):
  #   return ", ".join(str(v).strip().capitalize() for v in value)
  # v = str(value).replace(";", ",").replace("/", ",")
  # return ", ".join([s.strip().capitalize() for s in v.split(",") if s.strip()])
  
  if isinstance(value, (list, np.ndarray)):
    cleaned = [str(v).strip().capitalize() for v in value if str(v).strip()]
    return ", ".join(cleaned) if cleaned else None

  v = str(value).replace(";", ",").replace("/", ",")
  parts = [s.strip().capitalize() for s in v.split(",") if s.strip()]
  return ", ".join(parts) if parts else None


# for col in ['qualities', 'values', 'defects', 'interests']:
#     profiles[f"{col}_cleaned"] = profiles[col].apply(list_to_string)

# =====================================================
# 🔟 TAILLE & POIDS
# =====================================================

def extract_height_range(val):
  if pd.isna(val):
    return np.nan, np.nan, np.nan
  
  val = str(val).lower().strip()
  
  # Intervalle "X-Y" ou "X à Y"
  interval_match = re.findall(r'(\d+\.\d+)\s*(?:-|à)\s*(\d+\.\d+)', val)
  if interval_match:
    a, b = map(float, interval_match[0])
    mean = round((a + b)/2, 2)
    return a, b, mean
  
  # "plus de X" ou ">= X"
  plus_match = re.search(r'(?:plus de|>=)\s*(\d+\.\d+)', val)
  if plus_match:
    x = float(plus_match.group(1))
    return x, np.nan, np.nan
  
  # "moins de X"
  moins_match = re.search(r'(?:moins de)\s*(\d+\.\d+)', val)
  if moins_match:
    x = float(moins_match.group(1))
    return np.nan, x, np.nan
  
  # Valeur simple "X m"
  number_match = re.search(r'\d+\.\d+', val)
  if number_match:
    x = float(number_match.group())
    return x, x, x
  
  return np.nan, np.nan, np.nan

def extract_weight_range(val):
  if pd.isna(val):
    return np.nan, np.nan, np.nan
  
  val = str(val).lower().strip()
  
  # Intervalle "X-Y" ou "X à Y"
  interval_match = re.findall(r'(\d+)\s*(?:-|à)\s*(\d+)', val)
  if interval_match:
    a, b = map(float, interval_match[0])
    mean = round((a + b)/2, 2)
    return a, b, mean
  
  # "> X" ou "plus de X"
  plus_match = re.search(r'(?:plus de|>)\s*(\d+)', val)
  if plus_match:
    x = float(plus_match.group(1))
    return x, np.nan, np.nan
  
  # "< X" ou "moins de X"
  moins_match = re.search(r'(?:moins de|<)\s*(\d+)', val)
  if moins_match:
    x = float(moins_match.group(1))
    return np.nan, x, np.nan
  
  # Valeur simple "X kg"
  number_match = re.search(r'\d+', val)
  if number_match:
    x = float(number_match.group())
    return x, x, x
  
  # "moyenne" ou autre texte
  return np.nan, np.nan, np.nan

# profiles[['height_min', 'height_max', 'height_mean']] = profiles['height'].apply(
#     lambda x: pd.Series(extract_height_range(x))
# )
# profiles[['weight_min', 'weight_max', 'weight_mean']] = profiles['weight'].apply(
#     lambda x: pd.Series(extract_weight_range(x))
# )

# =====================================================
# 11️⃣ APPARENCE PHYSIQUE
# =====================================================

def clean_physical_appearance(val):
  if val is None or pd.isna(val):
    return ""
  
  val = str(val).strip()
  
  # supprimer toutes les lettres séparées par des virgules et/ou espaces
  # ex: 'c, o, r, p, u, l, e' -> 'corpule'
  val = re.sub(r'([a-zA-Z])\s*,\s*', r'\1', val)  # remplace chaque lettre suivie de virgule par la lettre seule
  
  # mettre en minuscules
  val = val.lower()
  
  # retirer accents
  val = unidecode.unidecode(val)
  
  # supprimer espaces multiples
  val = re.sub(r'\s+', ' ', val).strip()
  
  return val

# appliquer
# profiles['physical_appearance_cleaned'] = profiles['physical_appearance'].apply(clean_physical_appearance)

# =====================================================
# 12 PHYSICAL APPEARANCE, ECONOMIC SITUATION, EDUCATION LEVEL, RELATIONSHIP GOAL
# =====================================================

def prepare_for_embedding(text):
    """
    Nettoie les valeurs textuelles en préparation pour les embeddings :
    - Convertit en chaîne de caractères
    - Met en minuscules
    - Supprime accents et ponctuation légère
    - Supprime crochets, guillemets, caractères spéciaux
    - Supprime espaces multiples
    """
    if text is None or pd.isna(text):
        return ""
    
    # Convertir en texte
    text = str(text).strip()
    
    # Supprimer accents
    text = unidecode.unidecode(text)
    
    # Minuscule
    text = text.lower()
    
    # Supprimer crochets, guillemets, doubles quotes, etc.
    text = re.sub(r"[\[\]'\"’]", "", text)
    
    # Supprimer les caractères non alphabétiques de remplissage (ex: \\)
    text = re.sub(r"\\", "", text)
    
    # Supprimer les doubles espaces et ponctuations excessives
    text = re.sub(r"\s+", " ", text)
    
    # Supprimer ponctuations inutiles en bout de phrase
    text = re.sub(r"[.,;:!?-]+$", "", text)
    
    return text.strip()

# Exemple d'application sur une colonne
# profiles['physical_appearance_cleaned'] = profiles['physical_appearance'].apply(clean_physical_appearance)
# profiles['economic_cleaned'] = profiles['economic_situation'].apply(prepare_for_embedding)
# profiles['education_level_cleaned'] = profiles['education_level'].apply(prepare_for_embedding)
# profiles['relationship_goal_cleaned'] = profiles['relationship_goal'].apply(prepare_for_embedding)

def remove_suffixes(df):
  """
  Renomme automatiquement les colonnes du DataFrame en retirant
  les suffixes _cleaned, _normalized, _grouped, etc.
  """
  suffixes = ["_cleaned", "_normalized", "_grouped"]
  rename_map = {}

  for col in df.columns:
    new_col = col
    for suf in suffixes:
      new_col = re.sub(f"{suf}$", "", new_col)
    rename_map[col] = new_col

  return df.rename(columns=rename_map)
