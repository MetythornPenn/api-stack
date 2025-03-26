# app/services/redis.py
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings


class RedisService:
    """Service for interacting with Redis."""
    
    def __init__(self) -> None:
        self.redis_url = settings.REDIS_URI
        self.client: Optional[redis.Redis] = None
    
    async def connect(self) -> redis.Redis:
        """Connect to Redis."""
        if self.client is None:
            self.client = redis.from_url(
                self.redis_url, 
                encoding="utf-8", 
                decode_responses=True
            )
        return self.client
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def get(self, key: str) -> Any:
        """Get a value from Redis."""
        client = await self.connect()
        return await client.get(key)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set a value in Redis with optional expiration."""
        client = await self.connect()
        return await client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """Delete a key from Redis."""
        client = await self.connect()
        return await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        client = await self.connect()
        return await client.exists(key) > 0


# Create a singleton instance
redis_service = RedisService()



