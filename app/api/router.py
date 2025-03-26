
# app/api/router.py
from fastapi import APIRouter

from app.api.v1.items import router as items_router
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(items_router.router, prefix="/items", tags=["items"])
