from typing import Dict, Any, List

def transform_profile_data(ad_data: Dict[str, Any]) -> List[Dict[str, Any]]:
  profiles = []
  ad_id = ad_data['ad_id']
  
  # Profile ADVERTISER
  advertiser = ad_data['profiles']['advertiser']
  advertiser_profile = {
    'id': 2*ad_id, # f"{ad_id}-ADVERTISER",
    'ad_id': ad_id,
    'profile_type': 'ADVERTISER',
    'name': advertiser.get('NAME'),
    'religion': advertiser.get('RELIGION'),
    'age': advertiser.get('AGE'),
    'sex': advertiser.get('SEX'),
    'country_of_residence': advertiser.get('COUNTRY_OF_RESIDENCE'),
    'country_of_origin': advertiser.get('COUNTRY_OF_ORIGIN', [None])[0] if advertiser.get('COUNTRY_OF_ORIGIN') else None,
    'region_of_origin': advertiser.get('REGION_OF_ORIGIN', [None])[0] if advertiser.get('REGION_OF_ORIGIN') else None,
    'village_of_origin': advertiser.get('VILLAGE_OF_ORIGIN'),
    'sector_of_activity': advertiser.get('SECTOR_OF_ACTIVITY'),
    'marital_status': advertiser.get('MARITAL_STATUS'),
    'has_children': advertiser.get('HAS_CHILDREN') == 'Oui' if advertiser.get('HAS_CHILDREN') else False,
    'number_of_children': advertiser.get('NUMBER_OF_CHILDREN'),
    'qualities': advertiser.get('QUALITIES', []),
    'values': advertiser.get('VALUES', []),
    'defects': advertiser.get('DEFECTS', []),
    'interests': advertiser.get('INTERESTS', []),
    'height': advertiser.get('HEIGHT'),
    'weight': advertiser.get('WEIGHT'),
    'physical_appearance': advertiser.get('PHYSICAL_APPEARANCE'),
    'economic_situation': advertiser.get('ECONOMIC_SITUATION'),
    'education_level': advertiser.get('EDUCATION_LEVEL'),
    'illness': advertiser.get('ILLNESS'),
    'relationship_goal': advertiser.get('RELATIONSHIP', [None])[0] if advertiser.get('RELATIONSHIP') else None
  }
  profiles.append(advertiser_profile)
  
  # Profile DESIRED
  desired = ad_data['profiles']['desired']
  desired_profile = {
    'id': 2*ad_id + 1, # f"{ad_id}-DESIRED",
    'ad_id': ad_id,
    'profile_type': 'DESIRED',
    'name': desired.get('NAME'),
    'religion': desired.get('RELIGION'),
    'age': desired.get('AGE'),
    'sex': desired.get('SEX'),
    'country_of_residence': desired.get('COUNTRY_OF_RESIDENCE'),
    'country_of_origin': desired.get('COUNTRY_OF_ORIGIN', [None])[0] if desired.get('COUNTRY_OF_ORIGIN') else None,
    'region_of_origin': desired.get('REGION_OF_ORIGIN', [None])[0] if desired.get('REGION_OF_ORIGIN') else None,
    'village_of_origin': desired.get('VILLAGE_OF_ORIGIN'),
    'sector_of_activity': desired.get('SECTOR_OF_ACTIVITY'),
    'marital_status': desired.get('MARITAL_STATUS'),
    'has_children': desired.get('HAS_CHILDREN') == 'Oui' if desired.get('HAS_CHILDREN') else False,
    'number_of_children': desired.get('NUMBER_OF_CHILDREN'),
    'qualities': desired.get('QUALITIES', []),
    'values': desired.get('VALUES', []),
    'defects': desired.get('DEFECTS', []),
    'interests': desired.get('INTERESTS', []),
    'height': desired.get('HEIGHT'),
    'weight': desired.get('WEIGHT'),
    'physical_appearance': ', '.join(desired.get('PHYSICAL_APPEARANCE', [])) if desired.get('PHYSICAL_APPEARANCE') else None,
    'economic_situation': desired.get('ECONOMIC_SITUATION'),
    'education_level': desired.get('EDUCATION_LEVEL'),
    'illness': desired.get('ILLNESS'),
    'relationship_goal': desired.get('RELATIONSHIP', [None])[0] if desired.get('RELATIONSHIP') else None
  }
  profiles.append(desired_profile)
  
  return profiles
