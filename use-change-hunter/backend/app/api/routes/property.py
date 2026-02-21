from fastapi import APIRouter

router = APIRouter()


@router.get("/{property_id}")
async def get_property(property_id: str):
    """Get property details"""
    return {"property_id": property_id}


@router.post("")
async def create_property(data: dict):
    """Create a new property entry"""
    return {"id": "new_id", "data": data}
