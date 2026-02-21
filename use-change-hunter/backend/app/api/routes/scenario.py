from fastapi import APIRouter

router = APIRouter()


@router.get("/{property_id}")
async def get_scenarios(property_id: str):
    """Get scenarios for a property"""
    return {"property_id": property_id, "scenarios": []}


@router.post("/{property_id}")
async def create_scenario(property_id: str, data: dict):
    """Create a new scenario for a property"""
    return {"property_id": property_id, "scenario": data}
