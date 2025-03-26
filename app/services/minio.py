
# app/services/minio.py
import io
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from fastapi import UploadFile
import aiohttp
from minio import Minio, S3Error
from minio.commonconfig import CopySource

from app.core.config import settings


class MinioService:
    """Service for interacting with MinIO / S3 storage."""
    
    def __init__(self) -> None:
        parsed_url = urlparse(f"http://{settings.MINIO_SERVER}:{settings.MINIO_PORT}")
        self.client = Minio(
            f"{parsed_url.netloc}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,  # Set to True for HTTPS
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
    
    async def ensure_bucket_exists(self) -> None:
        """Ensure the default bucket exists."""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
    
    async def upload_file(
        self,
        file: UploadFile,
        object_name: Optional[str] = None,
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Upload a file to MinIO.
        
        Args:
            file: The file to upload
            object_name: The name to give the object in the bucket
            bucket_name: The bucket to upload to (defaults to settings.MINIO_BUCKET_NAME)
            content_type: The content type of the file
            metadata: Additional metadata for the object
            
        Returns:
            The URL of the uploaded file
        """
        await self.ensure_bucket_exists()
        
        bucket = bucket_name or self.bucket_name
        object_name = object_name or file.filename
        
        if not object_name:
            raise ValueError("Object name must be provided")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Set content type if not provided
        if not content_type:
            content_type = file.content_type
        
        # Upload to MinIO
        self.client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=io.BytesIO(content),
            length=file_size,
            content_type=content_type,
            metadata=metadata,
        )
        
        # Build URL to the file
        return f"http://{settings.MINIO_SERVER}:{settings.MINIO_PORT}/{bucket}/{object_name}"
    
    async def get_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> io.BytesIO:
        """
        Get a file from MinIO.
        
        Args:
            object_name: The name of the object in the bucket
            bucket_name: The bucket to get from (defaults to settings.MINIO_BUCKET_NAME)
            
        Returns:
            A BytesIO object containing the file data
        """
        bucket = bucket_name or self.bucket_name
        
        response = self.client.get_object(
            bucket_name=bucket,
            object_name=object_name,
        )
        
        data = io.BytesIO()
        for d in response.stream(32 * 1024):
            data.write(d)
        data.seek(0)
        
        return data
    
    async def delete_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            object_name: The name of the object in the bucket
            bucket_name: The bucket to delete from (defaults to settings.MINIO_BUCKET_NAME)
            
        Returns:
            True if the file was deleted, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        
        try:
            self.client.remove_object(
                bucket_name=bucket,
                object_name=object_name,
            )
            return True
        except S3Error:
            return False
    
    async def list_files(
        self,
        prefix: Optional[str] = None,
        bucket_name: Optional[str] = None,
        recursive: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        List files in a bucket.
        
        Args:
            prefix: Filter objects by prefix
            bucket_name: The bucket to list from (defaults to settings.MINIO_BUCKET_NAME)
            recursive: Whether to list recursively
            
        Returns:
            A list of objects in the bucket
        """
        bucket = bucket_name or self.bucket_name
        
        objects = self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=recursive,
        )
        
        result = []
        for obj in objects:
            result.append({
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified,
                "etag": obj.etag,
                "content_type": obj.content_type,
            })
        
        return result


# Create a singleton instance
minio_service = MinioService()
