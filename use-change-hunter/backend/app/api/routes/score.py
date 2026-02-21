from fastapi import APIRouter

router = APIRouter()


@router.get("/{property_id}")
async def get_score(property_id: str):
    """Get property opportunity score"""
    return {"property_id": property_id, "score": 0.0}


@router.post("/{property_id}/calculate")
async def calculate_score(property_id: str):
    """Calculate opportunity score for a property"""
    return {"property_id": property_id, "score": 0.0}
