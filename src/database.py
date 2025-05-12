import logging
import os
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from src.core.config import get_settings
import datetime

settings = get_settings()
logger = logging.getLogger(__name__)

class FirestoreDatabase:
    """Firestore database connection manager."""
    
    def __init__(self, collection_name):
        self.client = firestore.Client(database=settings.FIRESTORE_DB_NAME)
        self.collection_name = collection_name
        self.collection = self.get_collection()

    def get_collection(self):
        """Get Firestore collection reference."""
        return self.client.collection(self.collection_name)

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        doc = self.collection.document(document_id).get()
        return doc.to_dict() if doc.exists else None

    def list_documents(
        self,  
        query: Dict[str, Any] = None,
        sort_by: str = "created_at", 
        sort_direction: str = "DESCENDING",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List documents with optional query, sorting, and pagination."""
        query_ref = self.collection
        
        if query:
            for key, value in query.items():
                query_ref = query_ref.where(key, "==", value)

        query_ref = query_ref.order_by(sort_by, direction=firestore.Query.DESCENDING if sort_direction == "DESCENDING" else firestore.Query.ASCENDING).limit(limit)

        def fix_timestamp(doc_dict):
            """Convert Firestore timestamps to JSON-serializable format."""
            for key, value in doc_dict.items():
                if isinstance(value, datetime.datetime):  # Firestore timestamp
                    doc_dict[key] = value.isoformat()  # Convert to ISO string
            return doc_dict

        return [fix_timestamp(doc.to_dict()) for doc in query_ref.stream()]

    def add_document(self, data: Dict[str, Any], document_id:str = None) -> str:
        """Add a document to a collection and return the document ID."""
        data["created_at"] = firestore.SERVER_TIMESTAMP
        data["updated_at"] = firestore.SERVER_TIMESTAMP
        if document_id == None:
            response = self.collection.add(data)
            document_id = response[1].id
        else:
            self.collection.document(document_id).set(data)
        return document_id  # Firestore returns (document, reference)

    def update_document(self, document_id: str, data: Dict[str, Any]) -> None:
        """Update an existing document."""
        data["updated_at"] = firestore.SERVER_TIMESTAMP
        self.collection.document(document_id).update(data)

    def delete_document(self, document_id: str) -> None:
        """Delete a document by ID."""
        self.collection.document(document_id).delete()

# Global database instance
db = FirestoreDatabase(get_settings().FIRESTORE_COLLECTION_NAME)
