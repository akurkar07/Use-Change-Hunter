from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.geocode_client import GeocodeClient
from app.db.models import OpportunityScore, Property, StrategyType
from app.db.session import get_db
from app.schemas.api import ScoreCalculateRequest
from app.services.planning_service import search_nearby_planning
from app.services.scoring_service import calculate_opportunity_score

router = APIRouter()
geocode = GeocodeClient()

@router.get("/{property_id}")
async def get_score(
    property_id: str,
    strategy: str = "opportunity",
    db: AsyncSession = Depends(get_db),
):
    """Get latest score for a property and strategy."""
    try:
        prop_uuid = UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property_id")

    try:
        strategy_enum = StrategyType(strategy)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid strategy type")

    result = await db.execute(
        select(OpportunityScore)
        .where(
            OpportunityScore.property_id == prop_uuid,
            OpportunityScore.strategy_type == strategy_enum,
        )
        .order_by(OpportunityScore.generated_at.desc())
    )
    score = result.scalars().first()
    if not score:
        raise HTTPException(status_code=404, detail="No score found for property/strategy")

    return {
        "property_id": property_id,
        "strategy_type": score.strategy_type.value,
        "score_total": score.score_total,
        "score_risk": score.score_risk,
        "score_confidence": score.score_confidence,
        "breakdown": score.breakdown,
        "generated_at": score.generated_at.isoformat(),
    }


@router.post("/{property_id}/calculate")
async def calculate_score(
    property_id: str,
    payload: ScoreCalculateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Calculate and persist score for a property."""
    try:
        prop_uuid = UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property_id")

    prop_result = await db.execute(select(Property).where(Property.id == prop_uuid))
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    lat = None
    lon = None
    if prop.geom and prop.geom.startswith("POINT(") and prop.geom.endswith(")"):
        point = prop.geom[6:-1].strip().split()
        if len(point) == 2:
            lon = float(point[0])
            lat = float(point[1])

    if lat is None or lon is None:
        geocode_query = prop.postcode or prop.address
        if not geocode_query:
            raise HTTPException(status_code=400, detail="Property has no location data")
        location = await geocode.geocode(geocode_query, prop.postcode)
        if not location:
            raise HTTPException(status_code=404, detail="Could not geocode property location")
        lat = location["lat"]
        lon = location["lon"]

    _, summary = await search_nearby_planning(
        db=db,
        lat=lat,
        lon=lon,
        radius_m=payload.radius_m,
        strategy=payload.strategy,
    )

    score_result = await calculate_opportunity_score(
        property_id=property_id,
        db=db,
        factors={"precedent_summary": summary, "strategy": payload.strategy},
        strategy_type="opportunity",
    )

    score = OpportunityScore(
        id=uuid4(),
        property_id=prop_uuid,
        strategy_type=StrategyType.opportunity,
        score_total=score_result["score_total"],
        score_risk=score_result["score_risk"],
        score_confidence=score_result["score_confidence"],
        breakdown=score_result["breakdown"],
        scenario={"strategy": payload.strategy, "radius_m": payload.radius_m},
    )
    db.add(score)
    await db.commit()

    return {
        "property_id": property_id,
        "strategy_type": payload.strategy,
        "score_total": score.score_total,
        "score_risk": score.score_risk,
        "score_confidence": score.score_confidence,
        "breakdown": score.breakdown,
    }
