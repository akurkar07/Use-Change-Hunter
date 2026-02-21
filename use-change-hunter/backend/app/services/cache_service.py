import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import IbexCache

# Redis client (lazy initialized)
_redis: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Initialize Redis client (singleton)"""
    global _redis
    if _redis is None:
        _redis = await redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


def hash_payload(payload: dict) -> str:
    """Generate deterministic cache key from payload"""
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


async def get_cached_hybrid(
    key: str,
    db: AsyncSession,
    allow_expired: bool = False
) -> Optional[dict]:
    """
    Hybrid cache retrieval: Redis (fast) → Database (persistent)
    
    Args:
        key: Cache key
        db: Database session for fallback
        allow_expired: If True, return expired cache entries
    
    Returns:
        Cached data or None
    """
    try:
        # Try Redis first (fastest)
        redis_client = await get_redis_client()
        cached_value = await redis_client.get(key)
        if cached_value:
            return json.loads(cached_value)
    except Exception as e:
        # Redis failure - log and continue to DB
        print(f"Redis retrieval failed for key {key}: {e}")
    
    try:
        # Fallback to database
        cache_entry = await db.query(IbexCache).filter(
            IbexCache.cache_key == key
        ).first()
        
        if not cache_entry:
            return None
        
        # Check expiration
        if cache_entry.expires_at and datetime.utcnow() > cache_entry.expires_at:
            if not allow_expired:
                return None
        
        return cache_entry.response_json
    except Exception as e:
        print(f"Database cache retrieval failed for key {key}: {e}")
        return None


async def set_cached_hybrid(
    key: str,
    payload: dict,
    response: dict,
    db: AsyncSession,
    ttl_seconds: int = 86400
) -> bool:
    """
    Hybrid cache storage: Redis (fast) + Database (persistent)
    
    Args:
        key: Cache key
        payload: Original request payload
        response: Response to cache
        db: Database session
        ttl_seconds: Time-to-live in seconds (default 24 hours)
    
    Returns:
        True if at least one cache layer succeeded
    """
    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    redis_success = False
    db_success = False
    
    # Store in Redis (fast, expires automatically)
    try:
        redis_client = await get_redis_client()
        await redis_client.set(
            key,
            json.dumps(response),
            ex=ttl_seconds
        )
        redis_success = True
    except Exception as e:
        print(f"Redis cache write failed for key {key}: {e}")
    
    # Store in database (persistent, survives Redis restart)
    try:
        cache_entry = IbexCache(
            cache_key=key,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            payload_json=payload,
            response_json=response
        )
        db.add(cache_entry)
        await db.commit()
        db_success = True
    except Exception as e:
        print(f"Database cache write failed for key {key}: {e}")
        await db.rollback()
    
    return redis_success or db_success


async def invalidate_cache(key: str, db: AsyncSession) -> None:
    """Remove cache entry from both Redis and database"""
    try:
        redis_client = await get_redis_client()
        await redis_client.delete(key)
    except Exception as e:
        print(f"Redis invalidation failed for key {key}: {e}")
    
    try:
        await db.query(IbexCache).filter(IbexCache.cache_key == key).delete()
        await db.commit()
    except Exception as e:
        print(f"Database cache invalidation failed for key {key}: {e}")
        await db.rollback()


async def cleanup_expired_cache(db: AsyncSession) -> int:
    """Remove expired entries from database (Redis auto-expires)"""
    try:
        result = await db.query(IbexCache).filter(
            IbexCache.expires_at <= datetime.utcnow()
        ).delete()
        await db.commit()
        return result
    except Exception as e:
        print(f"Cache cleanup failed: {e}")
        await db.rollback()
        return 0