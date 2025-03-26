
# app/api/v1/items/utils.py
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.items.models import Item


async def check_item_exists(
    db: AsyncSession,
    item_id: UUID,
) -> bool:
    """
    Check if an item exists.
    
    Args:
        db: Database session
        item_id: ID of the item to check
        
    Returns:
        True if the item exists, False otherwise
    """
    query = select(Item).where(Item.id == item_id)
    result = await db.execute(query)
    return result.scalars().first() is not None


async def check_item_owner(
    db: AsyncSession,
    item_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Check if a user is the owner of an item.
    
    Args:
        db: Database session
        item_id: ID of the item to check
        user_id: ID of the user to check
        
    Returns:
        True if the user is the owner, False otherwise
    """
    query = select(Item).where(
        Item.id == item_id,
        Item.owner_id == user_id,
    )
    result = await db.execute(query)
    return result.scalars().first() is not None