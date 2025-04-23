<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from routers import upload
from services.authentication_service import AuthService
from core.config import get_settings
from services.authentication_service import AuthService
from core.middleware.auth import AuthenticationMiddleware
=======
from fastapi import FastAPI
from routers import search
from src.discon_analyzer.router import router as discon_analyzer_router

>>>>>>> 38fbaab5f3fb3d8db9bae90c4a5e92ace3f91a6e


app = FastAPI(title="JISEBI Document Processing API", description="Upload document and get your evaluation")
settings = get_settings()

# Create auth service instance
auth_service = AuthService(settings)

# Add the authentication middleware
app.add_middleware(
    AuthenticationMiddleware,
    auth_service=auth_service,
    exclude_paths=["/docs", "/redoc", "/openapi.json", "/health", "/metrics"]
)

# Register Routers
<<<<<<< HEAD
app.include_router(upload.router, prefix="/api", tags=["Search"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Journal Search API"}
=======
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(discon_analyzer_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Journal Search API", 
        "docs" : "/docs"
        }
>>>>>>> 38fbaab5f3fb3d8db9bae90c4a5e92ace3f91a6e
