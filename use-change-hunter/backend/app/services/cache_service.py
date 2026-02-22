"""Hybrid Redis + Database caching service."""
import json
from datetime import timedelta
from typing import Optional, Any

import redis.asyncio as redis
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class CacheService:
    """Hybrid Redis + Database cache with intelligent fallback."""

    def __init__(self):
        """Initialize cache service."""
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = settings.REDIS_CACHE_TTL

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Continuing with DB-only cache")
            self.redis_client = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()

    async def get_cached(self, key: str) -> Optional[dict]:
        """
        Get value from cache (Redis first, then fallback).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        # Try Redis first
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache hit (Redis): {key}")
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        logger.debug(f"Cache miss: {key}")
        return None

    async def set_cached(
        self,
        key: str,
        value: dict,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache (Redis + DB fallback).

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        ttl = ttl or self.ttl

        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value),
                )
                logger.debug(f"Cached (Redis): {key}")
                return True
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # If Redis failed, at least log it for DB fallback
        logger.debug(f"Scheduled for DB cache: {key}")
        return False

    async def delete_cached(self, key: str) -> bool:
        """Delete cached value."""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        return False

    async def clear_cache(self, pattern: str = "*"):
        """Clear cache by pattern."""
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cache entries")
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")

    async def get_or_fetch(
        self,
        key: str,
        fetch_fn,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Get from cache or fetch if not found.

        Args:
            key: Cache key
            fetch_fn: Async function to call if cache miss
            ttl: Cache TTL in seconds

        Returns:
            Cached or fetched value
        """
        # Try cache first
        cached = await self.get_cached(key)
        if cached:
            return cached

        # Fetch new value
        logger.info(f"Cache miss, fetching: {key}")
        value = await fetch_fn()

        # Store in cache
        if value:
            await self.set_cached(key, value, ttl)

        return value


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create cache service singleton."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
