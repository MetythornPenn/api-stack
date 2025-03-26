
# app/services/ratelimit.py
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.services.redis import redis_service


class RateLimiter:
    """
    Rate limiting service using Redis.
    """
    
    def __init__(
        self,
        redis_prefix: str = "ratelimit:",
        requests: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ):
        self.redis_prefix = redis_prefix
        self.requests = requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
    
    async def is_rate_limited(self, key: str) -> Tuple[bool, int, int]:
        """
        Check if a key is rate limited.
        
        Args:
            key: The key to check
            
        Returns:
            A tuple of (is_limited, current_usage, limit)
        """
        if not settings.RATE_LIMIT_ENABLED:
            return False, 0, self.requests
        
        redis_key = f"{self.redis_prefix}{key}"
        client = await redis_service.connect()
        
        # Get current count and TTL
        pipe = client.pipeline()
        await pipe.incr(redis_key)
        await pipe.ttl(redis_key)
        count, ttl = await pipe.execute()
        
        # Set expiry if this is the first request
        if ttl < 0:
            await client.expire(redis_key, self.window_seconds)
            ttl = self.window_seconds
        
        is_limited = count > self.requests
        return is_limited, count, self.requests
    
    async def reset(self, key: str) -> None:
        """Reset the rate limit for a key."""
        redis_key = f"{self.redis_prefix}{key}"
        client = await redis_service.connect()
        await client.delete(redis_key)


# Create a function for use as a dependency
def rate_limit(
    requests: Optional[int] = None,
    window_seconds: Optional[int] = None,
    key_func: Optional[Callable[[Request], str]] = None,
):
    """
    Dependency for rate limiting.
    
    Args:
        requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        key_func: Function to generate the rate limit key from the request
    """
    limiter = RateLimiter(
        requests=requests,
        window_seconds=window_seconds,
    )
    
    async def _rate_limit(request: Request, response: Response) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        
        # Generate key based on client IP by default
        key = key_func(request) if key_func else request.client.host
        
        is_limited, current, limit = await limiter.is_rate_limited(key)
        
        # Set rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
        
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
    
    return _rate_limit