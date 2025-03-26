from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.base_class import Base


class Item(Base):
    """
    Item model with vector embedding support for PostgreSQL.
    
    Note: Vector field will be created using Alembic migration with pgvector extension.
    """
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    
    # Vector embedding - This will be handled in migration for PostgreSQL
    # For Oracle, it would be implemented differently
    # embedding = Column(ARRAY(Float), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # MinIO storage reference
    image_path = Column(String(512), nullable=True)