from fastapi import Depends, HTTPException, Request, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.core.config import settings

# Define a configurable rate limiter based on settings
ConfigurableRateLimiter = RateLimiter(
    times=settings.RATE_LIMIT_PER_SECOND,
    seconds=1,
)


async def rate_limit_dependency(request: Request):
    """
    Dependency for rate limiting API endpoints.
    
    This will be applied to routes where rate limiting is needed.
    Rate limiting is only applied if enabled in settings.
    
    Args:
        request: FastAPI request object
    """
    if settings.RATE_LIMIT_ENABLED:
        # Only apply rate limiting if enabled
        limiter_dependency = Depends(ConfigurableRateLimiter)
        await limiter_dependency(request)