from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResponse(BaseModel):
    query: str
    strategy: str
    center: Dict[str, float]
    radius_m: int
    summary: Dict[str, Any]
    opportunities: List[Dict[str, Any]]


class CreatePropertyRequest(BaseModel):
    address: Optional[str] = None
    postcode: Optional[str] = None
    property_type: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class ScoreCalculateRequest(BaseModel):
    strategy: str = "extension"
    radius_m: int = Field(default=1000, ge=100, le=5000)


class ScenarioRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scenario_type: str = "development"
    parameters: Dict[str, Any]
