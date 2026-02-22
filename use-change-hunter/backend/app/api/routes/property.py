from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.geocode_client import GeocodeClient
from app.db.models import OpportunityScore, Property, Scenario
from app.db.session import get_db
from app.schemas.api import CreatePropertyRequest

router = APIRouter()
geocode = GeocodeClient()

@router.get("/{property_id}")
async def get_property(property_id: str, db: AsyncSession = Depends(get_db)):
    """Get property details with latest scoring and scenarios."""
    try:
        prop_uuid = UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property_id")

    prop_result = await db.execute(select(Property).where(Property.id == prop_uuid))
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    score_result = await db.execute(
        select(OpportunityScore)
        .where(OpportunityScore.property_id == prop_uuid)
        .order_by(OpportunityScore.generated_at.desc())
    )
    scores = score_result.scalars().all()

    scenario_result = await db.execute(
        select(Scenario)
        .where(Scenario.property_id == prop_uuid)
        .order_by(Scenario.created_at.desc())
    )
    scenarios = scenario_result.scalars().all()

    return {
        "property": {
            "id": str(prop.id),
            "address": prop.address,
            "postcode": prop.postcode,
            "property_type": prop.property_type,
            "geom": prop.geom,
        },
        "scores": [
            {
                "id": str(s.id),
                "strategy_type": s.strategy_type.value,
                "score_total": s.score_total,
                "score_risk": s.score_risk,
                "score_confidence": s.score_confidence,
                "breakdown": s.breakdown,
                "generated_at": s.generated_at.isoformat(),
            }
            for s in scores
        ],
        "scenarios": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "scenario_type": s.scenario_type,
                "parameters": s.parameters,
                "results": s.results,
                "created_at": s.created_at.isoformat(),
            }
            for s in scenarios
        ],
    }


@router.post("")
async def create_property(data: CreatePropertyRequest, db: AsyncSession = Depends(get_db)):
    """Create a property entry."""
    lat = data.lat
    lon = data.lon
    if (lat is None or lon is None) and (data.address or data.postcode):
        geocode_query = data.address or data.postcode or ""
        location = await geocode.geocode(geocode_query, data.postcode)
        if location:
            lat = location["lat"]
            lon = location["lon"]

    prop = Property(
        id=uuid4(),
        address=data.address,
        postcode=data.postcode,
        property_type=data.property_type,
        geom=f"POINT({lon} {lat})" if lat is not None and lon is not None else None,
    )
    db.add(prop)
    await db.commit()
    await db.refresh(prop)

    return {
        "id": str(prop.id),
        "address": prop.address,
        "postcode": prop.postcode,
        "property_type": prop.property_type,
        "geom": prop.geom,
    }
