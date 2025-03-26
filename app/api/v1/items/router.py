
# app/api/v1/items/router.py
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_superuser
from app.api.v1.auth.schemas import UserOut
from app.api.v1.items.schemas import (
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemUpdate,
)
from app.api.v1.items.service import item_service
from app.core.db import get_db
from app.services.ratelimit import rate_limit

router = APIRouter()


@router.get(
    "",
    response_model=ItemListResponse,
    summary="Get all items",
    dependencies=[Depends(rate_limit())],
)
async def get_items(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    owner_id: Optional[UUID] = None,
) -> ItemListResponse:
    """
    Get all items with pagination.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return
    - **owner_id**: Optional filter for items by owner
    """
    items = await item_service.get_multi(
        db,
        skip=skip,
        limit=limit,
        owner_id=owner_id,
    )
    total = await item_service.count(db, owner_id=owner_id)
    
    return ItemListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new item",
    dependencies=[Depends(rate_limit())],
)
async def create_item(
    item_in: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
) -> ItemResponse:
    """
    Create new item.
    
    - **name**: Name of the item
    - **description**: Optional description
    - **price**: Price of the item (must be greater than 0)
    - **image_url**: Optional URL to item image
    """
    item = await item_service.create(
        db,
        obj_in=item_in,
        owner_id=UUID(current_user.id),
    )
    return item


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID",
    dependencies=[Depends(rate_limit())],
)
async def get_item(
    item_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """
    Get an item by ID.
    
    - **item_id**: The ID of the item to retrieve
    """
    item = await item_service.get(db, id=item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    return item


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update item",
    dependencies=[Depends(rate_limit())],
)
async def update_item(
    item_in: ItemUpdate,
    item_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
) -> ItemResponse:
    """
    Update an item.
    
    - **item_id**: The ID of the item to update
    - **name**: Optional new name
    - **description**: Optional new description
    - **price**: Optional new price (must be greater than 0)
    - **image_url**: Optional new URL to item image
    """
    item = await item_service.get(db, id=item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check ownership or superuser status
    if item.owner_id != UUID(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    item = await item_service.update(
        db,
        db_obj=item,
        obj_in=item_in,
    )
    
    return item


@router.delete(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Delete item",
    dependencies=[Depends(rate_limit())],
)
async def delete_item(
    item_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_active_user),
) -> ItemResponse:
    """
    Delete an item.
    
    - **item_id**: The ID of the item to delete
    """
    item = await item_service.get(db, id=item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Check ownership or superuser status
    if item.owner_id != UUID(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    item = await item_service.delete(db, id=item_id)
    return item
