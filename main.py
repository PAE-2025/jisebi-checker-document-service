from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routers import upload
from services.authentication_service import AuthService
from core.config import get_settings
from services.authentication_service import AuthService
from core.middleware.auth import AuthenticationMiddleware

from helpers.jisebi_reporting import rendur


app = FastAPI(title="JISEBI Document Processing API", description="Upload document and get your evaluation")
settings = get_settings()

# Create auth service instance
auth_service = AuthService(settings)

# Add the authentication middleware
app.add_middleware(
    AuthenticationMiddleware,
    auth_service=auth_service,
    exclude_paths=["/docs", "/redoc", "/openapi.json", "/health", "/metrics", "/redocc"]
)

# Register Routers
app.include_router(upload.router, prefix="/api", tags=["Search"])

@app.get("/redocc")
async def root():
    return HTMLResponse(await rendur())