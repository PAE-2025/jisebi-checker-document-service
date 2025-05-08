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
    
    class Config:
        env_file = env_file
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()