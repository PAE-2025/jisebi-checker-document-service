import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

# First load the .env file to get the environment
load_dotenv()

# Then load the appropriate environment-specific file
env_file = f".env"
load_dotenv(env_file)

class Settings(BaseSettings):
    AUTH_SERVICE_URL: str
    PLATFORM: str
    MONGODB_URI: str
    JWT_SECRET: str

    # Task processor settings
    WORKER_SLEEP_TIME: int = 1  # seconds to sleep when no tasks are found
    ERROR_SLEEP_TIME: int = 5   # seconds to sleep after an error
    PROCESSING_TIME: int = 5    # seconds to simulate task processing (for demo)
    
    # Task statuses
    STATUS_QUEUED: str = "on_queue"
    STATUS_PROCESSING: str = "processing"
    STATUS_COMPLETED: str = "completed"
    STATUS_FAILED: str = "failed"
    STATUS_CANCELLED: str = "cancelled"
    # Google Cloud Storage settings
    FIRESTORE_DB_NAME: str
    FIRESTORE_COLLECTION_NAME: str

    class Config:
        env_file = env_file
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()