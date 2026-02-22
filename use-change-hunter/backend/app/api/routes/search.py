from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.geocode_client import GeocodeClient
from app.db.session import get_db
from app.schemas.api import SearchResponse
from app.services.planning_service import search_nearby_planning

router = APIRouter()
geocode = GeocodeClient()

@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    strategy: str = Query("extension"),
    radius_m: int = Query(1000, ge=100, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """Search planning precedents around a postcode/address."""
    location = await geocode.geocode(q)
    if not location:
        raise HTTPException(status_code=404, detail="Could not geocode query")

    lat = location["lat"]
    lon = location["lon"]
    _, summary = await search_nearby_planning(
        db=db,
        lat=lat,
        lon=lon,
        radius_m=radius_m,
        strategy=strategy,
    )

    return {
        "query": q,
        "strategy": strategy,
        "center": {"lat": lat, "lon": lon},
        "radius_m": radius_m,
        "summary": summary,
        "opportunities": summary.get("precedents", []),
    }
