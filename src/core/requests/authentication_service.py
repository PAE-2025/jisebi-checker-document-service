import httpx
from typing import Dict, Any, Tuple, Optional
import logging
from fastapi import Depends

from src.core.config import get_settings, Settings

logger = logging.getLogger(__name__)

class AuthService:
    """Service for communicating with the authentication API"""
    
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.auth_service_url = settings.AUTH_SERVICE_URL
        self.timeout = 5.0  # 5 seconds timeout for auth requests
    
    async def validate_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate a token with the authentication service
        
        Args:
            token: The authentication token to validate
            
        Returns:
            Tuple of (is_valid, user_info)
            - is_valid: Boolean indicating if token is valid
            - user_info: User information if token is valid, None otherwise
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.auth_service_url}/auth/verify-token",
                    headers={"Authorization": token},
                    timeout=self.timeout
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                data = response.json()
                logger.warning(data)
                is_valid = data.get("status", False)
                user_info = data.get("data", {}).get("user") if is_valid else None
                
                return is_valid, user_info
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Auth service returned error: {e.response.status_code} - {e.response.text}")
                return False, None
                
            except httpx.RequestError as e:
                logger.error(f"Error contacting auth service: {str(e)}")
                raise Exception(f"Authentication service unavailable: {str(e)}")