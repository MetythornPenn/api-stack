
# app/api/v1/items/models.py
import uuid
from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Item(BaseModel):
    """
    Item model.
    """
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(512), nullable=True)
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    owner = relationship("User", back_populates="items")
