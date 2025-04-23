# import httpx
# from fastapi import Depends
# from ..core.config import get_settings, Settings

# class SemanticService:

#     def __init__(
#         self, 
#         http_client: httpx.AsyncClient = Depends(),
#         settings: Settings = Depends(get_settings)
#     ):
#         self.http_client = http_client
#         self.base_url = settings.SEMANTIC_CHECKING_SERVICE_URL
        
#     async def fetch_data(self, params: dict):
#         response = await self.http_client.get(f"{self.base_url}/data", params=params)
#         response.raise_for_status()
#         return response.json()