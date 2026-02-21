from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from uuid import uuid4

from app.clients.ibex_client import IBEXClient
from app.services.cache_service import hash_payload, get_cached_hybrid, set_cached_hybrid

ibex = IBEXClient()


async def create_scenario(
    property_id: str,
    db: AsyncSession,
    parameters: Dict
) -> Optional[dict]:
    """
    Create a "what-if" scenario for a property
    
    Scenarios allow users to test different development/investment strategies
    with custom parameters. Results are cached based on property + parameters.
    
    Args:
        property_id: UUID of property
        db: Database session
        parameters: Scenario parameters (e.g., density increases, use changes)
    
    Returns:
        Scenario analysis result from IBEX API (cached)
    """
    logger.info(f"Creating scenario for property {property_id} with params {parameters}")
    
    payload = {
        "property_id": property_id,
        "scenario_type": parameters.get("scenario_type", "base"),
        "parameters": parameters
    }
    
    cache_key = "ibex:scenario:" + hash_payload(payload)
    
    # Check if scenario already calculated and cached
    cached = await get_cached_hybrid(cache_key, db)
    if cached:
        logger.info(f"Cache hit for scenario: {cache_key}")
        return cached
    
    logger.info(f"Cache miss for scenario: {cache_key}, calling API...")
    
    # Call IBEX for scenario analysis
    response = await ibex.post_search(payload)
    
    if response:
        await set_cached_hybrid(cache_key, payload, response, db)
        logger.info(f"Cached scenario result for {cache_key}")
    
    return response


async def compare_scenarios(
    property_id: str,
    db: AsyncSession,
    scenario_list: list
) -> Optional[Dict]:
    """
    Compare multiple scenarios for a property
    
    Args:
        property_id: UUID of property
        db: Database session
        scenario_list: List of scenario parameter dicts to compare
    
    Returns:
        Comparison analysis with all scenarios
    """
    logger.info(f"Comparing {len(scenario_list)} scenarios for property {property_id}")
    
    results = {}
    for i, scenario_params in enumerate(scenario_list):
        result = await create_scenario(property_id, db, scenario_params)
        results[f"scenario_{i}"] = result
    
    return results


async def optimize_scenario(
    property_id: str,
    db: AsyncSession,
    optimization_objective: str = "roi"
) -> Optional[dict]:
    """
    Find optimal scenario parameters for a property
    
    Args:
        property_id: UUID of property
        db: Database session
        optimization_objective: What to optimize for (roi, sustainability, development_time)
    
    Returns:
        Optimized scenario parameters and projected results
    """
    logger.info(f"Optimizing scenario for property {property_id} (objective={optimization_objective})")
    
    payload = {
        "property_id": property_id,
        "optimization_type": optimization_objective,
        "optimize": True
    }
    
    cache_key = "ibex:scenario_opt:" + hash_payload(payload)
    
    cached = await get_cached_hybrid(cache_key, db)
    if cached:
        logger.info(f"Cache hit for scenario optimization: {cache_key}")
        return cached
    
    response = await ibex.post_search(payload)
    
    if response:
        await set_cached_hybrid(cache_key, payload, response, db)
    
    return response
