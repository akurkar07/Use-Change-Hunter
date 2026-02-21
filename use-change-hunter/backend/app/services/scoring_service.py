from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.clients.ibex_client import IBEXClient
from app.services.cache_service import hash_payload, get_cached_hybrid, set_cached_hybrid

ibex = IBEXClient()


async def calculate_opportunity_score(
    property_id: str,
    db: AsyncSession,
    factors: Dict = None,
    strategy_type: str = "opportunity"
) -> Optional[dict]:
    """
    Calculate opportunity score based on various factors
    
    Uses hybrid cache to avoid redundant IBEX API calls for the same property/strategy
    
    Args:
        property_id: UUID of property
        db: Database session
        factors: Optional custom scoring factors
        strategy_type: Type of strategy (opportunity, risk, development, sustainability)
    
    Returns:
        Scoring result with detailed breakdown
    """
    logger.info(f"Calculating {strategy_type} score for property {property_id}")
    
    if factors is None:
        factors = {}
    
    payload = {
        "property_id": property_id,
        "strategy_type": strategy_type,
        "factors": factors
    }
    
    cache_key = "ibex:score:" + hash_payload(payload)
    
    # Try cache first
    cached = await get_cached_hybrid(cache_key, db)
    if cached:
        logger.info(f"Cache hit for scoring query: {cache_key}")
        return cached
    
    logger.info(f"Cache miss for scoring query: {cache_key}, calling API...")
    
    # Call IBEX for scoring data
    response = await ibex.post_search(payload)
    
    if response:
        await set_cached_hybrid(cache_key, payload, response, db)
        logger.info(f"Cached scoring result for {cache_key}")
    
    return response


async def calculate_risk_score(
    property_id: str,
    db: AsyncSession,
    risk_model: str = "balanced"
) -> Optional[dict]:
    """
    Calculate risk factors and risk score
    
    Args:
        property_id: UUID of property
        db: Database session
        risk_model: Risk assessment model (conservative, balanced, aggressive)
    
    Returns:
        Risk analysis from IBEX API (cached)
    """
    logger.info(f"Calculating risk score for property {property_id} (model={risk_model})")
    
    return await calculate_opportunity_score(
        property_id,
        db,
        factors={"risk_model": risk_model},
        strategy_type="risk"
    )


async def calculate_sustainability_score(
    property_id: str,
    db: AsyncSession,
    include_carbon: bool = True
) -> Optional[dict]:
    """
    Calculate sustainability metrics and score
    
    Args:
        property_id: UUID of property
        db: Database session
        include_carbon: Include carbon footprint analysis
    
    Returns:
        Sustainability analysis from IBEX API (cached)
    """
    logger.info(f"Calculating sustainability score for property {property_id}")
    
    return await calculate_opportunity_score(
        property_id,
        db,
        factors={"include_carbon": include_carbon},
        strategy_type="sustainability"
    )
