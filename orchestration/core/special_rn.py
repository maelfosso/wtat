import re
from typing import Optional, List

def extract_ads_from_special_rn(publication: str) -> Optional[List[str]]:
  pattern = r'(?m)^[ \t]*[^a-zA-Z0-9\n\r]{5,}[ \t]*$'
  sections = re.split(pattern, publication)
  sections = [section.strip() for section in sections if section.strip()]
  return [sections[1]]
