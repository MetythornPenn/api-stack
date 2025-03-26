import io
from typing import BinaryIO, Optional, Union

from miniopy_async import Minio
from miniopy_async.commonconfig import ComposeSource
from miniopy_async.error import S3Error

from app.core.config import settings

# Initialize MinIO client
minio_client = Minio(
    f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


async def ensure_bucket_exists(bucket_name: str = settings.MINIO_BUCKET) -> None:
    """
    Ensure that the bucket exists. If not, create it.
    
    Args:
        bucket_name: Name of the bucket to check/create
    """
    try:
        bucket_exists = await minio_client.bucket_exists(bucket_name)
        if not bucket_exists:
            await minio_client.make_bucket(bucket_name)
    except S3Error as e:
        # Log the error but don't raise to avoid breaking the app
        print(f"Error ensuring bucket exists: {e}")


async def upload_file(
    file: Union[BinaryIO, bytes, str],
    object_name: str,
    bucket_name: str = settings.MINIO_BUCKET,
    content_type: Optional[str] = None,
) -> str:
    """
    Upload a file to MinIO storage.
    
    Args:
        file: File object, bytes, or string content to upload
        object_name: Name of the object in the bucket (path)
        bucket_name: Name of the bucket
        content_type: Content type of the file
        
    Returns:
        Object path in storage
    """
    # Ensure bucket exists
    await ensure_bucket_exists(bucket_name)
    
    # Prepare the data
    if isinstance(file, (bytes, str)):
        # For bytes or string content
        if isinstance(file, str):
            file = file.encode('utf-8')
        data = io.BytesIO(file)
        file_size = len(file)
    else:
        # For file objects
        data = file
        # Get file size
        data.seek(0, io.SEEK_END)
        file_size = data.tell()
        data.seek(0)
    
    # Upload the file
    await minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        length=file_size,
        content_type=content_type,
    )
    
    return f"{bucket_name}/{object_name}"


async def download_file(
    object_name: str, bucket_name: str = settings.MINIO_BUCKET
) -> bytes:
    """
    Download a file from MinIO storage.
    
    Args:
        object_name: Name of the object in the bucket (path)
        bucket_name: Name of the bucket
        
    Returns:
        File content as bytes
    """
    # Get the object
    response = await minio_client.get_object(bucket_name, object_name)
    
    # Read all data
    data = await response.read()
    await response.close()
    
    return data


async def get_presigned_url(
    object_name: str,
    bucket_name: str = settings.MINIO_BUCKET,
    expires: int = 3600,  # 1 hour
) -> str:
    """
    Generate a presigned URL for object download.
    
    Args:
        object_name: Name of the object in the bucket (path)
        bucket_name: Name of the bucket
        expires: URL expiration time in seconds
        
    Returns:
        Presigned URL
    """
    # Generate the URL
    url = await minio_client.presigned_get_object(
        bucket_name, object_name, expires=expires
    )
    
    return url


async def delete_file(object_name: str, bucket_name: str = settings.MINIO_BUCKET) -> None:
    """
    Delete a file from MinIO storage.
    
    Args:
        object_name: Name of the object in the bucket (path)
        bucket_name: Name of the bucket
    """
    # Delete the object
    await minio_client.remove_object(bucket_name, object_name)