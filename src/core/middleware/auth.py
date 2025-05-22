# app/core/middleware/auth.py
from fastapi import Request, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from typing import List
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from src.core.requests.authentication_service import AuthService
from src.core.config import get_settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        auth_service: AuthService,
        exclude_paths: List[str] = None
    ):
        super().__init__(app)
        self.auth_service = auth_service
        self.exclude_paths = exclude_paths or ["/docs"]
        self.audience = get_settings().SELF_URL
    
    async def dispatch(self, request: Request, call_next):
        try:

            if request.method == "OPTIONS":
                return await call_next(request)
            
            # Skip authentication for excluded paths
            if any(request.url.path.startswith(path) for path in self.exclude_paths):
                return await call_next(request)
            
            if request.url.path.startswith("/internal"):
                # Optionally verify Google OIDC token
                auth_header = request.headers.get("Authorization")
                # if not auth_header or not auth_header.startswith("Bearer "):
                #     raise HTTPException(status_code=401, detail="Missing or invalid authorization header for internal task")

                # token = auth_header.split(" ")[1]

                # # return await call_next(request)

                # try:
                #     id_info = id_token.verify_oauth2_token(
                #         token,
                #         google_requests.Request(),
                #         self.audience
                #     )

                #     # Optional: you can also check issuer, email, etc here if desired
                #     # if id_info["email"] != "expected-service-account@project.iam.gserviceaccount.com":
                #     #     raise HTTPException(status_code=403, detail="Unauthorized internal task source")

                # except Exception as e:
                #     print(f"OIDC token verification failed: {e}")
                #     raise HTTPException(status_code=403, detail="Invalid internal task identity")

                # All good, continue processing
                return await call_next(request)
            
            # Extract token from the request
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=401,
                    detail= {
                        "status": False,
                        "message":"Authorization header missing" 
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Validate with auth service
            try:
                token = auth_header
                is_valid, user_info = await self.auth_service.validate_token(token)

                logger.warning([is_valid, user_info])
                
                if not is_valid:
                    raise HTTPException(
                        status_code=401,
                        detail= {
                            "status": False,
                            "message": "Invalid or expired token"
                        },
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # Attach user info to request state for later use in route handlers
                request.state.user = user_info
                
            except HTTPException as e:
                # Re-raise HTTP exceptions
                raise
            except BaseException as e:
                logger.error(f"Authentication error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "status": False,
                        "message": "Authentication service error"
                    }
                )
        except HTTPException as e:
            origins = get_settings().ALLOWED_ORIGINS
            response = JSONResponse(status_code=e.status_code, 
                                    content={
                                        "status": "false",
                                        "message": e.detail}, 
                                    headers={
                                        "Access-Control-Allow-Headers": "access-control-allow-headers,access-control-allow-methods,access-control-allow-origin,authorization",
                                        "Access-Control-Allow-Origin": origins,
                                        "Access-Control-Allow-Credentials": "true",
                                        "Access-Control-Allow-Methods": "*",
                                        "Access-Control-Allow-Headers": "*",
                                    })
            return response
        
        # Continue processing the request
        return await call_next(request)


# Helper function to create and configure the middleware
def get_auth_middleware(app: ASGIApp, auth_service: AuthService = Depends()):
    return AuthenticationMiddleware(
        app=app,
        auth_service=auth_service,
        exclude_paths=["/docs", "/redoc", "/openapi.json", "/health", "/metrics"]
    )