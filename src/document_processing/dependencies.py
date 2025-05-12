from fastapi import Depends
from src.document_processing.service import JISEBIProcessingService

# Singleton instance of the analyzer service
_processing_service = None

def get_processing_service():
    """
    Dependency to get the analyzer service instance
    Uses a singleton pattern to avoid loading the NLP models multiple times
    """
    global _processing_service
    if _processing_service is None:
        _processing_service = JISEBIProcessingService()
    return _processing_service
