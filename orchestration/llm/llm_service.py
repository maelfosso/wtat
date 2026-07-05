from openai import AsyncOpenAI
import instructor
from typing import List, Dict
from .prompts import SYSTEM_MESSAGE, PROMPT_DUAL_PROFILES_EXTRACTION
from ..config import settings
from .models import DualProfiles

class LLMService:
  def __init__(self, config):
    raw_client = AsyncOpenAI(
      base_url=settings.llm_api_base,
      api_key=settings.llm_api_key
    )
    
    self.client = instructor.from_openai(raw_client, mode=instructor.Mode.JSON)
    self.model = settings.llm_model
    self.timeout = settings.llm_timeout
  
  async def extract_profile_from_single_ad(self, ad: Dict, context=None) -> DualProfiles:
    """Extrait les profiles depuis un seul ads"""

    if context:
      context.log.info(f"Debut de l'extraction des profiles pour l'ad {ad['id']}: {ad['ad'][:100]}")

    prompt = PROMPT_DUAL_PROFILES_EXTRACTION.replace("{ad_text}", ad['ad'])
    return await self.client.chat.completions.create(
      model=self.model,
      response_model=DualProfiles,
      max_retries=3,
      temperature=0.1,
      # max_tokens=20000,
      messages=[
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": prompt}
      ]
    )
