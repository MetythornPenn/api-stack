import json
from typing import Any, Optional

import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.config import settings


async def setup_cache() -> None:
    """
    Set up Redis cache for the application.
    """
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        encoding="utf8",
        decode_responses=True,
    )
    
    # Initialize FastAPI Cache with Redis backend
    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="fastapi-cache:",
        expire=settings.CACHE_EXPIRATION_SECONDS,
    )