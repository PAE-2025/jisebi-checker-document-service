from pymongo import AsyncMongoClient

from src.core.config import get_settings, Settings

connection_string: Settings = get_settings().MONGODB_URI

db = AsyncMongoClient(connection_string)["jisebi_documents"]

upload_collections = db["uploads"]


"""
Database connection and helper functions.
"""
import logging
from typing import Any, Dict, List, Optional
from pymongo import ASCENDING, DESCENDING

from src.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class Database:
    """MongoDB database connection manager."""
    client: Optional[AsyncMongoClient] = None
    db: Optional[Any] = None

    async def connect(self) -> None:
        """Connect to MongoDB database."""
        logger.info("Connecting to MongoDB...")
        self.client = AsyncMongoClient(settings.MONGODB_URI)
        self.db = self.client["jisebi_documents"]
        
        # Create indexes
        tasks_collection = self.get_collection("uploads")
        await tasks_collection.create_index([("created_at", ASCENDING)])
        await tasks_collection.create_index("status")
        # await tasks_collection.create_index([("priority", DESCENDING), ("created_at", ASCENDING)])
        
        logger.info("Connected to MongoDB")

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_collection(self, collection_name: str):
        """Get MongoDB collection."""
        if self.db is None:
            raise RuntimeError("Database connection not established")
        return self.db[collection_name]

    async def get_document(
        self, collection_name: str, document_id: str, key_name: str = "_id"
    ) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        collection = self.get_collection(collection_name)
        document = await collection.find_one({key_name: document_id})
        return document

    async def list_documents(
        self, 
        collection_name: str, 
        query: Dict[str, Any] = None,
        sort_by: str = "created_at", 
        sort_direction: int = -1,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List documents with pagination."""
        collection = self.get_collection(collection_name)
        cursor = collection.find(query or {})
        cursor.sort(sort_by, sort_direction).skip(skip).limit(limit)
        
        documents = []
        async for document in cursor:
            documents.append(document)
        
        return documents

# Global database instance
db = Database()