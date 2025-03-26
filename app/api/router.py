from fastapi import APIRouter

from app.api.v1.router import api_router as api_v1_router
from app.core.config import settings

router = APIRouter()

# Include versioned API routers
router.include_router(api_v1_router, prefix=settings.API_V1_STR)