import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from src.document_upload import router as document_upload_router
from src.core.requests.authentication_service import AuthService
from src.core.config import get_settings
from src.core.requests.authentication_service import AuthService
from src.core.middleware.auth import AuthenticationMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.database import db
from src.core.task_processor import task_processor

from src.document_upload.helpers.jisebi_reporting import rendur

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    logger.info("Application starting up...")
    # Start task processor
    await task_processor.start()
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    # Stop task processor
    await task_processor.stop()


app = FastAPI(title="JISEBI Document Processing API", description="Upload document and get your evaluation", lifespan=lifespan)

# Create auth service instance
auth_service = AuthService(settings)

# Allow requests from your frontend (Next.js on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

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