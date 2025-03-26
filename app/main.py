from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from loguru import logger
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import router as api_router
from app.core.cache import setup_cache
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup
    # Initialize Redis for rate limiting
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )
    await FastAPILimiter.init(redis)
    
    # Setup Redis cache
    await setup_cache()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    # Close Redis connections
    await redis.close()
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="FastAPI Production Boilerplate",
    description="Production-grade FastAPI application with PostgreSQL, pgvector, Redis, and MinIO",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

# Set CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Add request ID middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        # Add request ID to context if available
        if request_id:
            logger.bind(request_id=request_id)
            
        response = await call_next(request)
        return response


# Add middleware
app.add_middleware(RequestIDMiddleware)

# Include API router
app.include_router(api_router)


@app.get("/health", include_in_schema=True)
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn when script is executed directly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)