

# app/api/v1/items/schemas.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ItemBase(BaseModel):
    """
    Base schema for Item.
    """
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    image_url: Optional[HttpUrl] = None


class ItemCreate(ItemBase):
    """
    Schema for creating a new Item.
    """
    pass


class ItemUpdate(ItemBase):
    """
    Schema for updating an Item.
    """
    name: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)


class ItemResponse(ItemBase):
    """
    Schema for Item response.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """
    Schema for Item list response.
    """
    items: list[ItemResponse]
    total: int
    skip: int
    limit: int
