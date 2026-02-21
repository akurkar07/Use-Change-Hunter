from fastapi import APIRouter, Query
from typing import List

router = APIRouter()


@router.get("")
async def search(q: str = Query(..., min_length=1)):
    """Search for properties by location or address"""
    # Implementation here
    return {"results": []}
