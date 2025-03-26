from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service class with default methods to Create, Read, Update, Delete (CRUD).
    
    **Parameters**
    
    * `model`: A SQLAlchemy model class
    * `schema`: A Pydantic model (schema) class
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize service with the SQLAlchemy model.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            db: Database session
            id: ID of the record to get
            
        Returns:
            The model instance if found, None otherwise
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_count(self, db: AsyncSession) -> int:
        """
        Get total count of records.
        
        Args:
            db: Database session
            
        Returns:
            Total count of records
        """
        query = select(func.count()).select_from(self.model)
        result = await db.execute(query)
        return result.scalar()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Input data
            
        Returns:
            Created model instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Model instance to update
            obj_in: Input data
            
        Returns:
            Updated model instance
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        Delete a record.
        
        Args:
            db: Database session
            id: ID of the record to delete
            
        Returns:
            Deleted model instance if found, None otherwise
        """
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj