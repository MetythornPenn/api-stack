from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Shared properties
class ItemBase(BaseModel):
    """Base Item schema with common attributes."""
    
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    image_path: Optional[str] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    
    title: str
    # embedding can be added here if needed


# Properties to receive on item update
class ItemUpdate(ItemBase):
    """Schema for updating an existing item."""
    
    title: Optional[str] = None


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    """Base schema for items retrieved from the database."""
    
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties to return to client
class Item(ItemInDBBase):
    """Schema for items returned to the client."""
    pass


# Properties stored in DB
class ItemInDB(ItemInDBBase):
    """Schema for items as stored in the database."""
    pass


# For pagination responses
class ItemPage(BaseModel):
    """Schema for paginated item responses."""
    
    items: List[Item]
    total: int
    page: int
    size: int
    pages: int