"""Search endpoint - main entry point for property searches."""
from fastapi import APIRouter, HTTPException, Query, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.planning_service import get_planning_service
from app.services.scoring_service import get_scoring_service
from app.schemas.schemas import SearchResponse, PropertyResponse, OpportunityScoreResponse

router = APIRouter()


@router.get("/")
async def search_properties(
    postcode: str = Query(..., min_length=2, description="UK postcode or address"),
    strategy: str = Query("extension", description="Development strategy"),
    radius: int = Query(1000, ge=100, le=5000, description="Search radius in meters"),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search for properties with opportunity analysis.

    This endpoint performs client operations:
    1. Geocodes the postcode/address to lat/lon
    2. Searches nearby planning precedents
    3. Calculates opportunity scores
    4. Returns ranked results

    Args:
        postcode: Search location (postcode or address)
        strategy: Development strategy (extension, hmo, office_residential, retail_mixed, flats)
        radius: Search radius in meters (100-5000)
        db: Database session

    Returns:
        SearchResponse with properties and scores
    """
    try:
        logger.info(f"🔍 Search: {postcode}, {strategy}, {radius}m")

        # TODO: In production:
        # 1. Geocode the postcode to lat/lon
        # 2. Query database for properties in that area
        # 3. Score each property
        # 4. Return results

        # For now, return mock response with proper schema
        mock_response = SearchResponse(
            properties=[],
            scores={},
            total=0,
            offset=0,
        )

        return mock_response

    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
