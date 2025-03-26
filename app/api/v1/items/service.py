
# app/api/v1/items/service.py
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.items.models import Item
from app.api.v1.items.schemas import ItemCreate, ItemUpdate
from app.db.base import CRUDBase
from app.services.cache import cached, clear_cache_by_pattern


class ItemService(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """
    Service for Item operations.
    """
    
    @cached(namespace="items")
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Item]:
        """
        Get an Item by ID with caching.
        """
        return await super().get(db, id)
    
    @cached(namespace="items")
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[UUID] = None,
    ) -> List[Item]:
        """
        Get multiple Items with optional filtering by owner and caching.
        """
        query = select(Item)
        
        if owner_id:
            query = query.where(Item.owner_id == owner_id)
        
        return await super().get_multi(db, skip=skip, limit=limit, query=query)
    
    @cached(namespace="items")
    async def count(
        self,
        db: AsyncSession,
        *,
        owner_id: Optional[UUID] = None,
    ) -> int:
        """
        Count Items with optional filtering by owner and caching.
        """
        query = select(Item)
        
        if owner_id:
            query = query.where(Item.owner_id == owner_id)
        
        return await super().count(db, query=query)
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: ItemCreate,
        owner_id: Optional[UUID] = None,
    ) -> Item:
        """
        Create a new Item with optional owner.
        """
        obj_in_data = obj_in.model_dump()
        
        if owner_id:
            obj_in_data["owner_id"] = owner_id
        
        db_obj = Item(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Clear cache
        clear_cache_by_pattern("items:*")
        
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Item,
        obj_in: Union[ItemUpdate, Dict[str, Any]],
    ) -> Item:
        """
        Update an Item.
        """
        result = await super().update(db, db_obj=db_obj, obj_in=obj_in)
        
        # Clear cache
        clear_cache_by_pattern("items:*")
        
        return result
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        id: UUID,
    ) -> Optional[Item]:
        """
        Delete an Item.
        """
        result = await super().delete(db, id=id)
        
        # Clear cache
        clear_cache_by_pattern("items:*")
        
        return result


item_service = ItemService(Item)
