import re
from typing import List

def clean_text(text: str) -> str:
  """Nettoie le texte en normalisant les espaces et caractères spéciaux"""
  text = text.replace('\ufeff', '').replace('\r\n', '\n')
  text = re.sub(r'\n+', '\n', text)  # Supprime les sauts de ligne multiples
  text = text.strip()
  return text

def is_separator(line: str) -> bool:
  """Détermine si une ligne est un séparateur entre annonces"""
  line = line.strip()
  if not line:
    return True
  
  separator_patterns = [
  r'^-+$',    # Lignes avec uniquement des tirets
  r'^_{5,}$',   # Lignes avec uniquement des underscores
  r'^\.{5,}$',  # Lignes avec uniquement des points
  r'^\*{5,}$',  # Lignes avec uniquement des astérisques
  r'^={5,}$',   # Lignes avec uniquement des égal
  r'^🛑.*$',  # Lignes commençant par 🛑
  r'^🔴.*$',  # Lignes commençant par 🔴
  r'^🟡.*$',  # Lignes commençant par 🟡
  r'^________________________________$',  # Long trait
  r'^___________________$',    # Trait moyen
  ]
  return any(re.fullmatch(pattern, line) for pattern in separator_patterns)

def extract_ads_from_sunday_rn(post_content: str) -> List[str]:
  text = clean_text(post_content)
  lines = text.split('\n')
  ads = []
  current_ad = None
  buffer = []
  
  for line in lines:
    ad_match = re.match(r'^(?P<type>DJO|RESSE)\s*(?P<number>\d+)\b', line, re.IGNORECASE)
    if ad_match:
      if current_ad:
        current_ad['content'] = '\n'.join(buffer).strip()
        ads.append(current_ad)
        buffer = []
      current_ad = {
        'type': ad_match.group('type').upper(),
        'number': int(ad_match.group('number')),
        'content': line
      }
      continue
    if current_ad:
      if is_separator(line):
        current_ad['content'] = '\n'.join(buffer).strip()
        ads.append(current_ad)
        current_ad = None
        buffer = []
      else:
        buffer.append(line)
  
  if current_ad and buffer:
    current_ad['content'] = '\n'.join(buffer).strip()
    ads.append(current_ad)
  
  for ad in ads:
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', ad['content'], re.IGNORECASE)
    ad['email'] = email_match.group(0) if email_match else None
    ad['content'] = f"{ad['type']} {ad['number']}\n{ad['content'].strip()}"
  
  return [ad['content'] for ad in ads]
