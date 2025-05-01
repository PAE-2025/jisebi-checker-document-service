from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from document_upload import router as document_upload_router
from core.requests.authentication_service import AuthService
from core.config import get_settings
from core.requests.authentication_service import AuthService
from core.middleware.auth import AuthenticationMiddleware

from document_upload.helpers.jisebi_reporting import rendur


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
app.include_router(document_upload_router.router, prefix="/api", tags=["Search"])

@app.get("/redocc")
async def root():
    return HTMLResponse(await rendur())