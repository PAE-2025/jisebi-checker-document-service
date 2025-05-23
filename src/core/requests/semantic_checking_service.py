import httpx
from typing import Dict, Any, Tuple, Optional, List, Union
import logging
from fastapi import Depends

from src.core.config import get_settings, Settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SemanticCheckingService:
    """Service for communicating with the authentication API"""
    
    def __init__(self):
        self.auth_service_url = settings.SEMANTIC_CHECKING_SERVICE_URL
        self.timeout = 300.0

    async def post_request(self, endpoint: str, payload: dict):

        endpoint = endpoint if endpoint.startswith("/") else "/" + endpoint
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.auth_service_url}{endpoint}",
                    timeout=self.timeout,
                    json=payload
                )
                
                # Check if request was successful
                response.raise_for_status()

                # Explicitly raise an exception if status code is not 200
                if response.status_code != 200:
                    raise httpx.HTTPStatusError(f"Unexpected status code: {response.status_code}", request=response.request, response=response)
                
                data = response.json()
                
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                return False, None
    
    async def check_novelty(self, title: str, abstract: str):
        return await self.post_request('api/novelty/search', {
            "title": title,
            "abstract": abstract
        })
    
    async def check_discon(self, discussion: str, conclusion: str):
        return await self.post_request('api/discon/analyze-paper', {
            "discussion": discussion,
            "conclusion": conclusion
        })
    
    async def check_ner(self, text:str):
        return await self.post_request('api/ner/analyze', {
            "text": text
        })
    
    async def check_grammar(self, texts: Union[List[str], str]):
        return await self.post_request('api/grammar/process-text/', {
            "text": texts
        })
          