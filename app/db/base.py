# app/db/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a record by ID.
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        query: Optional[Select] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        """
        if query is None:
            query = select(self.model)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        db: AsyncSession,
        *,
        query: Optional[Select] = None,
    ) -> int:
        """
        Count records matching the query.
        """
        if query is None:
            query = select(func.count()).select_from(self.model)
        else:
            query = select(func.count()).select_from(query.subquery())
        
        result = await db.execute(query)
        return result.scalar() or 0

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: Union[CreateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Create a new record.
        """
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**obj_in_data)  # type: ignore
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update a record.
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType:
        """
        Delete a record by ID.
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        obj = result.scalars().first()
        
        if obj:
            await db.delete(obj)
            await db.commit()
            
        return obj


