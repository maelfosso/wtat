from typing import Dict, Any, List, Optional

def normalize_list_to_str(value: Any) -> Optional[str]:
  """
  Convertit une liste en chaîne de caractères (séparée par des virgules),
  ou retourne la valeur telle quelle si ce n'est pas une liste.
  Gère les valeurs None et les listes vides.
  """
  if value is None:
    return None
  if isinstance(value, list):
    # Filtrer les valeurs None/vide et convertir en chaîne
    filtered = [str(v).strip() for v in value if v is not None and str(v).strip()]
    return ", ".join(filtered) if filtered else None
  return str(value).strip() if str(value).strip() else None

def get_first_from_list_or_value(value: Any) -> Optional[str]:
  """
  Extrait le premier élément d'une liste, ou retourne la valeur directement si ce n'est pas une liste.
  """
  if value is None:
    return None
  if isinstance(value, list) and len(value) > 0:
    return str(value[0]).strip() if value[0] is not None else None
  return str(value).strip() if value is not None and str(value).strip() else None

def transform_profile_data(ad_data: Dict[str, Any]) -> List[Dict[str, Any]]:
  """
  Transforme les données brutes LLM (nouveau format) en profils tabulaires.
  Compatible avec l'ancien format si nécessaire.
  
  Format d'entrée attendu :
  {
    'ad_id': int,
    'profiles': {
      'advertiser': { ... },  # Structure LLM v2
      'desired': { ... }    # Structure LLM v2
    }
  }
  """
  profiles = []
  ad_id = ad_data['ad_id']
  
  for profile_type, raw_profile in [
    ('ADVERTISER', ad_data['profiles']['advertiser']),
    ('DESIRED', ad_data['profiles']['desired'])
  ]:
    # Mapping robuste des champs (nouveau format + fallback ancien format)
    profile = {
      'id': 2 * ad_id + (0 if profile_type == 'ADVERTISER' else 1),
      'ad_id': ad_id,
      'profile_type': profile_type,
      
      # Champs simples avec fallback sur ancien nom si nécessaire
      'name': raw_profile.get('NAME'),
      'religion': raw_profile.get('RELIGION'),
      'age': raw_profile.get('AGE'),
      'sex': raw_profile.get('SEX'),
      'height': raw_profile.get('HEIGHT'),
      'weight': raw_profile.get('WEIGHT'),
      'sector_of_activity': raw_profile.get('SECTOR_OF_ACTIVITY'),
      'marital_status': raw_profile.get('MARITAL_STATUS'),
      'has_children': raw_profile.get('HAS_CHILDREN') == 'Oui' if raw_profile.get('HAS_CHILDREN') else False,
      'number_of_children': raw_profile.get('NUMBER_OF_CHILDREN'),
      
      # ✅ NOUVEAU CHAMP : PRIMARY_COUNTRY_OF_RESIDENCE
      'primary_country_of_residence': raw_profile.get('PRIMARY_COUNTRY_OF_RESIDENCE'), 
      'country_of_residence': raw_profile.get('COUNTRY_OF_RESIDENCE'),
      
      # ✅ COUNTRY_OF_ORIGIN : gère liste (ancien) ou chaîne/null (nouveau)
      'country_of_origin': get_first_from_list_or_value(raw_profile.get('COUNTRY_OF_ORIGIN')),
      
      # ⚠️ REGION/VILLAGE : absents du nouveau format → None (ou extraction depuis OTHER_LOCATIONS_MENTIONED si métier le demande)
      'region_of_origin': None,  # Ancien champ supprimé du prompt LLM
      'village_of_origin': None,  # Ancien champ supprimé du prompt LLM
      
      # ✅ Champs listes → chaînes pour les TEXT (physical_appearance, etc.)
      'physical_appearance': normalize_list_to_str(raw_profile.get('PHYSICAL_APPEARANCE')),
      'economic_situation': normalize_list_to_str(raw_profile.get('ECONOMIC_SITUATION')),
      'education_level': normalize_list_to_str(raw_profile.get('EDUCATION_LEVEL')),
      'illness': normalize_list_to_str(raw_profile.get('ILLNESS')),
      
      # ✅ RELATIONSHIP : liste → premier élément ou chaîne
      'relationship_goal': get_first_from_list_or_value(raw_profile.get('RELATIONSHIP')),
      
      # ✅ Champs qui RESTENT des listes (VARCHAR[] dans DuckDB)
      'qualities': raw_profile.get('QUALITIES', []) if isinstance(raw_profile.get('QUALITIES'), list) else [],
      'values': raw_profile.get('VALUES', []) if isinstance(raw_profile.get('VALUES'), list) else [],
      'defects': raw_profile.get('DEFECTS', []) if isinstance(raw_profile.get('DEFECTS'), list) else [],
      'interests': raw_profile.get('INTERESTS', []) if isinstance(raw_profile.get('INTERESTS'), list) else [],
    }
    
    profiles.append(profile)
  
  return profiles
