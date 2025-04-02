from pydantic_settings import BaseSettings
    
class Settings(BaseSettings):
    APP_NAME: str = "Jisebi Checker"
    DEBUG_MODE: bool = True
    
    SPACY_MODEL: str = "en_core_web_sm"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    SCOPUS_API_KEY: str = "9154cf8331f01fe191dbde9e367ee426"

settings = Settings()