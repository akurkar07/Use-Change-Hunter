from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.clients.ibex_client import IBEXClient
from app.services.cache_service import hash_payload, get_cached_hybrid, set_cached_hybrid

ibex = IBEXClient()

STRATEGY_KEYWORDS: Dict[str, List[str]] = {
    "extension": ["extension", "loft", "rear", "side return", "dormer"],
    "hmo": ["hmo", "house in multiple occupation", "bedsit", "co-living"],
    "office_to_resi": ["office", "residential", "conversion", "change of use", "c3"],
    "retail_to_mixed": ["retail", "mixed use", "shop", "commercial", "upper floors"],
    "flats": ["flat", "apartments", "subdivision", "self-contained"],
}

STRATEGY_ALIASES: Dict[str, str] = {
    "loft": "extension",
    "rear_extension": "extension",
    "side_return": "extension",
    "house_to_hmo": "hmo",
    "house_to_flats": "flats",
    "office-resi": "office_to_resi",
    "office_to_residential": "office_to_resi",
    "office->resi": "office_to_resi",
    "retail_to_mixed_use": "retail_to_mixed",
}


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


def _parse_decision_status(app: Dict[str, Any]) -> str:
    decision = str(
        app.get("decision")
        or app.get("decision_status")
        or app.get("status")
        or ""
    ).lower()
    if "refus" in decision or "reject" in decision:
        return "refused"
    if "approv" in decision or "grant" in decision or "permit" in decision:
        return "approved"
    return "other"


def _parse_date(app: Dict[str, Any]) -> Optional[datetime]:
    raw_date = app.get("decision_date") or app.get("date") or app.get("validated")
    if not raw_date:
        return None
    raw = str(raw_date).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _extract_applications(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("applications", "results", "items", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _matches_strategy(app: Dict[str, Any], strategy: str) -> bool:
    normalized = STRATEGY_ALIASES.get(strategy.lower(), strategy.lower())
    keywords = STRATEGY_KEYWORDS.get(normalized, STRATEGY_KEYWORDS["extension"])
    haystack = " ".join(
        str(app.get(k, "")).lower()
        for k in ("proposal", "description", "type", "development_type", "title")
    )
    return any(keyword in haystack for keyword in keywords)


def summarize_precedents(
    applications: List[Dict[str, Any]],
    strategy: str,
) -> Dict[str, Any]:
    normalized = STRATEGY_ALIASES.get(strategy.lower(), strategy.lower())
    now = datetime.now(timezone.utc)
    matched: List[Dict[str, Any]] = []
    approved = 0
    refused = 0
    recent_approved = 0
    recent_refused = 0

    for app in applications:
        if not _matches_strategy(app, normalized):
            continue
        decision = _parse_decision_status(app)
        decision_dt = _parse_date(app)
        is_recent = bool(decision_dt and (now - decision_dt).days <= 730)

        if decision == "approved":
            approved += 1
            if is_recent:
                recent_approved += 1
        elif decision == "refused":
            refused += 1
            if is_recent:
                recent_refused += 1

        if len(matched) < 12:
            matched.append(
                {
                    "reference": app.get("reference") or app.get("application_number"),
                    "address": app.get("address"),
                    "proposal": app.get("proposal") or app.get("description"),
                    "decision": decision,
                    "decision_date": decision_dt.date().isoformat() if decision_dt else None,
                }
            )

    total_decided = approved + refused
    approval_rate = round((approved / total_decided) * 100, 1) if total_decided else 0.0

    return {
        "strategy": strategy,
        "normalized_strategy": normalized,
        "matched_precedents": approved + refused,
        "approved_similar": approved,
        "refused_similar": refused,
        "recent_approved": recent_approved,
        "recent_refused": recent_refused,
        "approval_rate_percent": approval_rate,
        "precedents": matched,
    }


async def search_nearby_planning(
    *,
    db: AsyncSession,
    lat: float,
    lon: float,
    radius_m: int,
    strategy: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    payload = {
        "analysis_type": "planning_search",
        "location": {"lat": lat, "lon": lon},
        "radius_m": radius_m,
        "include_geometry": True,
    }
    response = await ibex_search_cached(payload, db)
    if not response:
        return [], summarize_precedents([], strategy)

    applications = _extract_applications(response)
    summary = summarize_precedents(applications, strategy)
    return applications, summary


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
