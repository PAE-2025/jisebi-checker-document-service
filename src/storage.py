from google.cloud import storage
from src.core.config import get_settings
import os
import io

class GoogleStorage:

    def __init__(self, bucket_name):
        self.storage_client   = storage.Client()
        self.bucket_name      = bucket_name
        self.bucket           = self.ensure_bucket_exists()

    # Make sure the bucket exists
    def ensure_bucket_exists(self):
        try:
            bucket = self.storage_client.get_bucket(self.bucket_name)
        except Exception:
            bucket = self.storage_client.create_bucket(self.bucket_name)
        return bucket

    # Upload a file to a specific folder in the bucket
    def upload(self, file_content, folder_name: str, file_name: str) -> str:
        """Upload a file to a specific folder in the GCP bucket.
        
        Supports both `bytes` and `IO[bytes]` file content.
        """
        blob_path = f"{folder_name}/{file_name}"
        blob = self.bucket.blob(blob_path)

        if isinstance(file_content, io.IOBase):
            file_content.seek(0)
            blob.upload_from_file(file_content)
        else:
            raise TypeError("file_content must be an IO[bytes] object")
        
        return blob_path
    
    def download(self, file_path):
        blob = self.bucket.blob(file_path)
        file_bytes = blob.download_as_bytes()
        return io.BytesIO(file_bytes)

    # Delete a file from the bucket
    def delete(self, file_path):
        blob = self.bucket.blob(file_path)
        blob.delete()

storage = GoogleStorage(get_settings().GCS_BUCKET_NAME)