from openai import AsyncOpenAI
import json
import re
import httpx
import os
import asyncio
from typing import List, Dict
from .prompts_v3 import SYSTEM_MESSAGE, PROMPT_DUAL_PROFILES_EXTRACTION

class LLMService:
  def __init__(self, config):
    self.client = AsyncOpenAI(
      base_url=config['api_base'],
      api_key=config['api_key']
    )
    self.model = config['model']
    self.batch_size = config.get('batch_size', 10)
    self.max_concurrent_requests = config.get('max_concurrent_requests', 5)
    self.timeout = config.get('timeout', 300.0)
    self.support_batch = self.batch_size > 1
  
  async def extract_profile_from_single_ad(self, ad: Dict, context=None) -> Dict:
    """Extrait les profiles depuis un seul ads"""

    if context:
      context.log.info(f"Debut de l'extraction des profiles pour l'ad {ad['id']}: {ad['ad'][:100]}")

    prompt_content = PROMPT_DUAL_PROFILES_EXTRACTION.replace("{ad_text}", ad['ad'])
    context.log.info(prompt_content[:100])

    try:
      messages = [
        { "role": "system", "content": SYSTEM_MESSAGE },
        { 
          "role": "user",
          "content": [{
            "type": "text",
            "text": prompt_content
          }]
        }
      ]
      
      if context:
        context.log.debug(f"Envoi du prompt au LLM")

      response = await self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=0,
        # top_p=0.9,
        max_tokens=4000,
        timeout=None, # httpx.Timeout(self.timeout, connect=10.0)
        extra_body={
          "reasoning_effort": "low"
        },
        response_format={
          "type": "json_object"
        }
      )

      if context:
        context.log.debug("Reponse recue du LLM")
        context.log.debug(response.choices[0])

      raw_content = response.choices[0].message.content
      if not raw_content:
        context.log.info(response)
        context.log.error("Response LLM vide (conent et reasonning_content sont null)")
        return {"ad_id": ad['id'], "profiles": {}, "error": "empty_response"}

      result, stop_step = self.process_response(context, raw_content)

      if context:
        context.log.debug(f"Ad {ad['id']} traité - Profiles extraits:")
        context.log.debug(raw_content)
        context.log.debug(f"Stop step: {stop_step}")
        context.log.debug(result)

      return {"ad_id": ad["id"], "profiles": result['profiles']}
    except Exception as e:
      error_msg = f"Erreur LLM pour l'ad {ad['id']}: {str(e)}"
      if context:
        context.log.error(error_msg)
      
      return {"ad_id": ad["id"], "profiles": {}, "error": "error_msg"}
  
  async def extract_profiles(self, ads: List[Dict], context=None) -> List[Dict]:
    """Extrait les profiles depuis une liste d'ads avec support batch"""
    if context:
      context.log.info(f"🚀 Début de l'extraction des profiles pour {len(ads)} ads")
      context.log.debug(f"Configuration: batch_size={self.batch_size}, model={self.model}")
    
    if len(ads) <= self.batch_size or not self.support_batch:
      # Traitement séquentiel pour petits lots ou mode dev
      return await self._process_sequential(ads, context)
    else:
      # Traitement par lots asynchrone
      return await self._process_batch_async(ads, context)
  
  async def _process_sequential(self, ads: List[Dict], context=None) -> List[Dict]:
    """Traitement séquentiel des ads"""
    results = []
    
    for i, ad in enumerate(ads):
      if context:
        context.log.debug(f"📝 Traitement séquentiel de l'ad {i+1}/{len(ads)} (ID: {ad.get('ad_id')})")
      
      try:
        result = await self._process_single_ad(ad, context)
        results.append(result)
        
        if context:
          context.log.debug(f"✅ Ad {ad.get('ad_id')} traité avec succès")
          
      except Exception as e:
        error_msg = f"❌ Erreur sur l'ad {ad.get('ad_id')}: {str(e)}"
        if context:
          context.log.error(error_msg)
        else:
          context.log.error(error_msg)
        
        results.append({"ad_id": ad.get('ad_id'), "profiles": {}, "error": str(e)})
    
    return results
  
  async def _process_batch_async(self, ads: List[Dict], context=None) -> List[Dict]:
    """Traitement asynchrone par lots avec semaphore pour limiter la concurrence"""
    semaphore = asyncio.Semaphore(self.max_concurrent_requests)
    tasks = []
    
    if context:
      context.log.info(f"🔄 Démarrage du traitement batch asynchrone ({len(ads)} ads, {self.max_concurrent_requests} requêtes concurrentes)")
    
    # Création des tâches asynchrones
    for i in range(0, len(ads), self.batch_size):
      batch_ads = ads[i:i + self.batch_size]
      task = self._process_batch_with_semaphore(batch_ads, semaphore, context)
      tasks.append(task)
    
    # Exécution parallèle des batches
    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Agrégation des résultats
    results = []
    for i, batch_result in enumerate(batch_results):
      if isinstance(batch_result, Exception):
        if context:
          context.log.error(f"❌ Erreur sur le batch {i}: {str(batch_result)}")
        # Recours au traitement séquentiel pour ce batch
        start_idx = i * self.batch_size
        end_idx = start_idx + self.batch_size
        fallback_ads = ads[start_idx:end_idx]
        fallback_results = await self._process_sequential(fallback_ads, context)
        results.extend(fallback_results)
      else:
        results.extend(batch_result)
    
    if context:
      context.log.info(f"🎉 Extraction terminée: {len([r for r in results if r.get('profiles')])} profiles extraits avec succès")
    
    return results
  
  async def _process_batch_with_semaphore(self, batch_ads: List[Dict], semaphore, context=None) -> List[Dict]:
    """Traite un batch d'ads avec limitation de concurrence"""
    async with semaphore:
      return await self._process_single_batch(batch_ads, context)
  
  async def _process_single_batch(self, batch_ads: List[Dict], context=None) -> List[Dict]:
    """Traite un seul batch d'ads"""
    if context:
      context.log.debug(f"🔄 Traitement d'un batch de {len(batch_ads)} ads")
    
    prompts = []
    for ad in batch_ads:
      prompt_content = PROMPT_DUAL_PROFILES_EXTRACTION.format(ad_text=ad['ad'])
      prompts.append({
        "ad_id": ad["id"],
        "prompt": prompt_content,
        "post_type": ad.get('post_type', 'Unknown')
      })
    
    try:
      # Préparation des messages pour le batch
      messages = [
        {
          "role": "system", 
          "content": system_message
        },
        {
          "role": "user",
          "content": json.dumps([p['prompt'] for p in prompts])
        }
      ]
      
      if context:
        context.log.debug(f"📤 Envoi du batch au LLM ({len(prompts)} prompts)")
      
      # Appel au LLM
      response = await self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=0.1,
        top_p=0.9,
        max_tokens=20000,
        timeout=httpx.Timeout(self.timeout, connect=10.0)
      )
      
      if context:
        context.log.debug("📥 Réponse reçue du LLM")
      
      # Traitement de la réponse
      raw_content = response.choices[0].message.content
      processed_results = self._process_batch_response(raw_content, prompts, context)
      
      return processed_results
      
    except Exception as e:
      if context:
        context.log.error(f"❌ Erreur lors du traitement du batch: {str(e)}")
      raise
  
  async def _process_single_ad(self, ad: Dict, context=None) -> Dict:
    """Traite une seule ad"""
    try:
      prompt_content = PROMPT_DUAL_PROFILES_EXTRACTION.format(ad_text=ad['ad'])
      
      if context:
        context.log.debug(f"🔍 Traitement de l'ad {ad.get('ad_id')} (type: {ad.get('post_type')})")
      
      response = await self.client.chat.completions.create(
        model=self.model,
        messages=[
          {"role": "system", "content": SYSTEM_MESSAGE},
          {"role": "user", "content": prompt_content}
        ],
        temperature=0.1,
        top_p=0.9,
        max_tokens=20000,
        timeout=httpx.Timeout(self.timeout, connect=10.0)
      )
      
      result = self.process_response(response.choices[0].message.content)
      
      if context:
        context.log.debug(f"✅ Ad {ad.get('ad_id')} traité - Profils extraits: {len(result.get('desired', {}))}")
      
      return {"ad_id": ad["id"], "profiles": result}
      
    except Exception as e:
      error_msg = f"Erreur LLM pour l'ad {ad.get('ad_id')}: {str(e)}"
      if context:
        context.log.error(error_msg)
      return {"ad_id": ad.get('ad_id'), "profiles": {}, "error": error_msg}
  
  def _process_batch_response(self, raw_content: str, prompts: List[Dict], context=None) -> List[Dict]:
    """Traite la réponse batch du LLM"""
    results = []
    
    try:
      # Tentative de parsing JSON pour les réponses batch
      batch_data = json.loads(raw_content)
      
      if isinstance(batch_data, list) and len(batch_data) == len(prompts):
        for i, item in enumerate(batch_data):
          processed = self.process_response(json.dumps(item))
          results.append({
            "ad_id": prompts[i]["id"],
            "profiles": processed
          })
      else:
        # Fallback: traitement individuel
        if context:
          context.log.warning("Format de réponse batch non reconnu, fallback au traitement individuel")
        
        for i, prompt in enumerate(prompts):
          try:
            # Extraction de la partie correspondante
            pattern = r'\{[^}]*"advertiser"[^}]*"desired"[^}]*\}'
            matches = re.findall(pattern, raw_content)
            
            if i < len(matches):
              processed = self.process_response(matches[i])
            else:
              processed = {"advertiser": {}, "desired": {}}
              
            results.append({
              "ad_id": prompt["id"],
              "profiles": processed
            })
          except Exception as e:
            results.append({
              "ad_id": prompt["id"], 
              "profiles": {},
              "error": str(e)
            })
            
    except json.JSONDecodeError:
      if context:
        context.log.warning("Réponse batch non-JSON, utilisation du fallback")
      # Fallback au traitement regex
      return self._process_batch_with_regex(raw_content, prompts, context)
    
    return results
  
  def _process_batch_with_regex(self, raw_content: str, prompts: List[Dict], context=None) -> List[Dict]:
    """Traite la réponse batch avec regex en fallback"""
    results = []
    pattern = r'\{(?:[^{}]|\{[^{}]*\})*"advertiser"(?:[^{}]|\{[^{}]*\})*"desired"(?:[^{}]|\{[^{}]*\})*\}'
    matches = re.findall(pattern, raw_content, re.DOTALL)
    
    if context:
      context.log.debug(f"🔍 {len(matches)} objets JSON trouvés dans la réponse batch")
    
    for i, prompt in enumerate(prompts):
      if i < len(matches):
        try:
          json_data = json.loads(matches[i])
          results.append({
            "ad_id": prompt["id"],
            "profiles": json_data
          })
        except json.JSONDecodeError:
          results.append({
            "ad_id": prompt["id"],
            "profiles": {},
            "error": "Erreur de parsing JSON"
          })
      else:
        results.append({
          "ad_id": prompt["id"],
          "profiles": {},
          "error": "Réponse manquante dans le batch"
        })
    
    return results
  
  def process_response(self, context, raw: str) -> dict:
    """Processing a response"""
    default_response = {"profiles": {"advertiser": {}, "desired": {}}}

    try:
        context.log.info(f"Raw avant nettoyage: {raw}")
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()
        context.log.info(f"Raw après nettoyage: {raw}")
        json_data = json.loads(raw)

        # Vérifications de structure
        if not isinstance(json_data, dict):
            return default_response, 0
            
        if "profiles" not in json_data:
            return default_response, 1

        if not isinstance(json_data["profiles"], dict):
            return default_response, 2

        if "desired" not in json_data["profiles"] or "advertiser" not in json_data["profiles"]:
            return default_response, 4

        if not isinstance(json_data["profiles"]["desired"], dict) or not isinstance(json_data["profiles"]["advertiser"], dict):
            return default_response, 6
        
        return json_data, None
    except (json.JSONDecodeError, Exception) as e:
        context.log.error(f"Erreur lors du parsing JSON: {e}")
        context.log.debug(f"Raw reçu: {raw}")
        return default_response, str(e)

