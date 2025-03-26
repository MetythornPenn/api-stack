from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.item import Item, ItemCreate, ItemPage, ItemUpdate
from app.services.items import item_service
from app.utils.ratelimit import rate_limit_dependency

router = APIRouter()


@router.get(
    "/",
    response_model=ItemPage,
    summary="Get multiple items",
    dependencies=[Depends(rate_limit_dependency)],
)
async def get_items(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
) -> Any:
    """
    Retrieve items with pagination.
    """
    items = await item_service.get_multi(db=db, skip=skip, limit=limit)
    total = await item_service.get_count(db=db)
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.post(
    "/",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    summary="Create new item",
    dependencies=[Depends(rate_limit_dependency)],
)
async def create_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: ItemCreate,
    image: Optional[UploadFile] = File(None, description="Item image"),
) -> Any:
    """
    Create new item with optional image upload.
    """
    # Check if an item with the same title already exists
    item = await item_service.get_by_title(db=db, title=item_in.title)
    if item:
        raise HTTPException(
            status_code=400,
            detail="An item with this title already exists.",
        )
    
    return await item_service.create_with_image(db=db, obj_in=item_in, image=image)


@router.get(
    "/{id}",
    response_model=Item,
    summary="Get item by ID",
    dependencies=[Depends(rate_limit_dependency)],
)
async def get_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    """
    Get item by ID.
    """
    item = await item_service.get(db=db, id=id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )
    return item


@router.put(
    "/{id}",
    response_model=Item,
    summary="Update item",
    dependencies=[Depends(rate_limit_dependency)],
)
async def update_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    item_in: ItemUpdate,
    image: Optional[UploadFile] = File(None, description="Item image"),
) -> Any:
    """
    Update an item.
    """
    item = await item_service.get(db=db, id=id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )
    
    # Update the item
    item = await item_service.update(db=db, db_obj=item, obj_in=item_in)
    
    # If image is provided, upload it to MinIO
    if image:
        from app.utils.storage import upload_file
        
        file_path = f"items/{item.id}/{image.filename}"
        await upload_file(image.file, file_path, content_type=image.content_type)
        
        # Update the item with the image path
        item.image_path = file_path
        db.add(item)
        await db.commit()
        await db.refresh(item)
    
    return item


@router.delete(
    "/{id}",
    response_model=Item,
    summary="Delete item",
    dependencies=[Depends(rate_limit_dependency)],
)
async def delete_item(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    """
    Delete an item.
    """
    item = await item_service.get(db=db, id=id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )
    
    # If item has an image, delete it
    if item.image_path:
        from app.utils.storage import delete_file
        
        try:
            await delete_file(item.image_path)
        except Exception as e:
            # Log the error but continue with item deletion
            print(f"Error deleting file: {e}")
    
    return await item_service.remove(db=db, id=id)