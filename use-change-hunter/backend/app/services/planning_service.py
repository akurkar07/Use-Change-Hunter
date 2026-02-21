from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.clients.ibex_client import IBEXClient
from app.services.cache_service import hash_payload, get_cached_hybrid, set_cached_hybrid

ibex = IBEXClient()


async def ibex_search_cached(
    payload: dict,
    db: AsyncSession,
    ttl_seconds: int = 86400
) -> Optional[dict]:
    """
    Search IBEX API with hybrid caching (Redis + Database fallback)
    
    Cache strategy:
    1. Check Redis (fast, expires automatically)
    2. Fall back to database (persistent, survives restarts)
    3. If neither has it, call IBEX API (expensive, requires credits)
    
    Args:
        payload: IBEX search request payload
        db: Database session for persistent cache
        ttl_seconds: Cache TTL in seconds (default 24 hours)
    
    Returns:
        IBEX API response (from cache or fresh call)
    """
    cache_key = "ibex:search:" + hash_payload(payload)
    
    # Try hybrid cache first
    cached = await get_cached_hybrid(cache_key, db)
    if cached:
        logger.info(f"Cache hit for IBEX query: {cache_key}")
        return cached
    
    logger.info(f"Cache miss for IBEX query: {cache_key}, calling API...")
    
    # Call IBEX API
    response = await ibex.post_search(payload)
    
    if response:
        # Store in both Redis + Database
        await set_cached_hybrid(cache_key, payload, response, db, ttl_seconds)
        logger.info(f"Cached IBEX response for {cache_key}")
    
    return response


async def analyze_zoning(
    property_id: str,
    db: AsyncSession,
    address: Optional[str] = None,
    postcode: Optional[str] = None
) -> Optional[dict]:
    """
    Analyze zoning regulations and opportunities for a property
    
    Args:
        property_id: UUID of property to analyze
        db: Database session
        address: Property address (improves IBEX accuracy)
        postcode: Property postcode
    
    Returns:
        Zoning analysis from IBEX API (cached)
    """
    logger.info(f"Analyzing zoning for property {property_id}")
    
    payload = {
        "property_id": property_id,
        "analysis_type": "zoning",
        "address": address,
        "postcode": postcode
    }
    
    return await ibex_search_cached(payload, db)


async def analyze_development_potential(
    property_id: str,
    db: AsyncSession,
    square_meters: Optional[float] = None
) -> Optional[dict]:
    """
    Analyze development potential and planning constraints
    
    Args:
        property_id: UUID of property
        db: Database session
        square_meters: Property size for density calculations
    
    Returns:
        Development analysis from IBEX API (cached)
    """
    logger.info(f"Analyzing development potential for property {property_id}")
    
    payload = {
        "property_id": property_id,
        "analysis_type": "development",
        "square_meters": square_meters
    }
    
    return await ibex_search_cached(payload, db)


async def analyze_planning_history(
    property_id: str,
    db: AsyncSession,
    lookback_years: int = 5
) -> Optional[dict]:
    """
    Analyze recent planning history and approvals
    
    Args:
        property_id: UUID of property
        db: Database session
        lookback_years: How many years back to search
    
    Returns:
        Planning history from IBEX API (cached)
    """
    logger.info(f"Analyzing planning history for property {property_id}")
    
    payload = {
        "property_id": property_id,
        "analysis_type": "planning_history",
        "lookback_years": lookback_years
    }
    
    return await ibex_search_cached(payload, db)
