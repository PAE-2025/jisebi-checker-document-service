from fastapi import Depends
from src.document_upload.service import JISEBIUploadService

# Singleton instance of the analyzer service
_upload_service = None

def get_upload_service():
    """
    Dependency to get the analyzer service instance
    Uses a singleton pattern to avoid loading the NLP models multiple times
    """
    global _upload_service
    if _upload_service is None:
        _upload_service = JISEBIUploadService()
    return _upload_service
