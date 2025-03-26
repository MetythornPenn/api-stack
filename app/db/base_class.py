from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.future import select
from sqlalchemy.sql.expression import delete, update


@as_declarative()
class Base:
    """Base class for all database models."""
    
    id = Column(Integer, primary_key=True, index=True)
    __name__: str
    
    # Generate tablename automatically based on class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()