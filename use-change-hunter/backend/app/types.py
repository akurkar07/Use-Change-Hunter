"""Type definitions and Pydantic models."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Precedent(BaseModel):
    """Planning precedent data type."""

    reference: str
    proposal: str
    decision: str  # approved, refused, withdrawn
    date_decided: str
    distance_m: float
    lat: float
    lng: float


class ScoreBreakdown(BaseModel):
    """Score calculation breakdown."""

    precedents_found: int
    approved: int
    refused: int
    approval_rate: float
    nearby_schemes: int


class OpportunityScore(BaseModel):
    """Opportunity score result."""

    property_id: str
    score_total: float = Field(..., ge=0, le=100)
    score_risk: float = Field(..., ge=0, le=100)
    score_confidence: float = Field(..., ge=0, le=100)
    score_breakdown: Optional[ScoreBreakdown] = None
