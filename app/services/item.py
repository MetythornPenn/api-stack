from typing import List, Optional

from fastapi import UploadFile
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.base import BaseService
from app.utils.storage import upload_file


class ItemService(BaseService[Item, ItemCreate, ItemUpdate]):
    """Service for handling Item operations."""
    
    def __init__(self):
        super().__init__(Item)
    
    @cache(expire=settings.CACHE_EXPIRATION_SECONDS)
    async def get_by_title(self, db: AsyncSession, *, title: str) -> Optional[Item]:
        """
        Get an item by title.
        
        Args:
            db: Database session
            title: Item title to search for
            
        Returns:
            Item if found, None otherwise
        """
        query = select(Item).where(Item.title == title)
        result = await db.execute(query)
        return result.scalars().first()
    
    @cache(expire=settings.CACHE_EXPIRATION_SECONDS, namespace="items")
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        """
        Get multiple items with caching.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of items
        """
        # Override from base class to add caching
        return await super().get_multi(db=db, skip=skip, limit=limit)
    
    async def create_with_image(
        self, db: AsyncSession, *, obj_in: ItemCreate, image: Optional[UploadFile] = None
    ) -> Item:
        """
        Create a new item with an optional image.
        
        Args:
            db: Database session
            obj_in: Item data
            image: Optional image file
            
        Returns:
            Created item
        """
        # First create the item
        db_obj = await self.create(db=db, obj_in=obj_in)
        
        # If image is provided, upload it to MinIO
        if image:
            file_path = f"items/{db_obj.id}/{image.filename}"
            await upload_file(image.file, file_path, content_type=image.content_type)
            
            # Update the item with the image path
            db_obj.image_path = file_path
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj


# Create a singleton instance
item_service = ItemService()