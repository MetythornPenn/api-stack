
# app/services/cache.py
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar, cast

from fastapi import Depends, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from app.core.config import settings
from app.services.redis import redis_service

T = TypeVar('T')


def setup_cache() -> None:
    """Initialize FastAPI Cache with Redis backend."""
    client = redis_service.client
    
    if client and settings.CACHE_ENABLED:
        FastAPICache.init(
            RedisBackend(client),
            prefix="fastapi-cache:",
            expire=settings.CACHE_EXPIRE_SECONDS,
        )


def cached(
    expire: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
    namespace: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Cache decorator that respects the CACHE_ENABLED setting.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if not settings.CACHE_ENABLED:
            return func

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if FastAPICache.get_backend() is None:
                return await func(*args, **kwargs)
                
            return await cache(
                expire=expire or settings.CACHE_EXPIRE_SECONDS,
                key_builder=key_builder,
                namespace=namespace or func.__module__,
            )(func)(*args, **kwargs)
            
        return cast(T, wrapper)
    
    return decorator


def clear_cache_by_pattern(pattern: str) -> None:
    """
    Clear cache entries matching the given pattern.
    """
    if not settings.CACHE_ENABLED or not redis_service.client:
        return
        
    async def _clear() -> None:
        client = await redis_service.connect()
        prefix = FastAPICache.get_prefix()
        keys = await client.keys(f"{prefix}:{pattern}")
        
        if keys:
            await client.delete(*keys)
    
    import asyncio
    asyncio.create_task(_clear())
