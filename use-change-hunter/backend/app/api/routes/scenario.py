from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Property, Scenario
from app.db.session import get_db
from app.schemas.api import ScenarioRequest
from app.services.scenario_service import create_scenario

router = APIRouter()

@router.get("/{property_id}")
async def get_scenarios(property_id: str, db: AsyncSession = Depends(get_db)):
    """Get scenarios for a property."""
    try:
        prop_uuid = UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property_id")

    result = await db.execute(
        select(Scenario)
        .where(Scenario.property_id == prop_uuid)
        .order_by(Scenario.created_at.desc())
    )
    scenarios = result.scalars().all()

    return {
        "property_id": property_id,
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


@router.post("/{property_id}")
async def create_scenario_route(
    property_id: str,
    data: ScenarioRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create and store a new scenario for a property."""
    try:
        prop_uuid = UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property_id")

    prop_result = await db.execute(select(Property).where(Property.id == prop_uuid))
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    result = await create_scenario(property_id=property_id, db=db, parameters=data.parameters)
    scenario = Scenario(
        id=uuid4(),
        property_id=prop_uuid,
        name=data.name,
        description=data.description,
        scenario_type=data.scenario_type,
        parameters=data.parameters,
        results=result,
    )
    db.add(scenario)
    await db.commit()

    return {
        "property_id": property_id,
        "scenario": {
            "id": str(scenario.id),
            "name": scenario.name,
            "description": scenario.description,
            "scenario_type": scenario.scenario_type,
            "parameters": scenario.parameters,
            "results": scenario.results,
        },
    }
