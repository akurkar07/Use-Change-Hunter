"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# PROPERTY SCHEMAS
# ============================================================================


class PropertyBase(BaseModel):
    """Base property schema."""

    postcode: str
    address: str
    latitude: float
    longitude: float
    area_sqm: Optional[float] = None
    historic_use: Optional[str] = None
    listed_status: Optional[str] = None
    opportunity_strategies: list[str] = []


class PropertyCreate(PropertyBase):
    """Schema for creating a property."""

    pass


class PropertyUpdate(BaseModel):
    """Schema for updating a property."""

    address: Optional[str] = None
    area_sqm: Optional[float] = None
    historic_use: Optional[str] = None
    listed_status: Optional[str] = None
    opportunity_strategies: Optional[list[str]] = None


class PropertyResponse(PropertyBase):
    """Schema for property response."""

    id: str
    distance_nearest_precedent: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SCORING SCHEMAS
# ============================================================================


class ScoreBreakdown(BaseModel):
    """Breakdown of opportunity score calculation."""

    precedents_found: int
    approved: int
    refused: int
    approval_rate: float
    nearby_schemes: int


class OpportunityScoreBase(BaseModel):
    """Base score schema."""

    score_total: float = Field(..., ge=0, le=100)
    score_risk: float = Field(..., ge=0, le=100)
    score_confidence: float = Field(..., ge=0, le=100)
    score_breakdown: Optional[ScoreBreakdown] = None


class OpportunityScoreResponse(OpportunityScoreBase):
    """Schema for score response."""

    id: str
    property_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PRECEDENT SCHEMAS
# ============================================================================


class Precedent(BaseModel):
    """Planning precedent."""

    reference: str
    proposal: str
    decision: str  # approved, refused, withdrawn
    date_decided: str
    distance_m: float
    lat: float
    lng: float


class PrecedentsResponse(BaseModel):
    """Response for precedents endpoint."""

    precedents: list[Precedent]
    stats: dict = {}


# ============================================================================
# SCENARIO SCHEMAS
# ============================================================================


class ScenarioBreakdown(BaseModel):
    """Financial scenario breakdown."""

    estimated_arv: float
    estimated_cost: float
    estimated_profit: float
    roi_percent: float
    holding_months: int
    financing_cost: float


class ScenarioBase(BaseModel):
    """Base scenario schema."""

    name: str
    strategy: str
    development_cost: float
    holding_period_months: int
    finance_type: str  # cash, btl_mortgage, development_loan
    finance_rate: float = 0.0
    assumptions: Optional[str] = None


class ScenarioCreate(ScenarioBase):
    """Schema for creating scenario."""

    property_id: str


class ScenarioUpdate(BaseModel):
    """Schema for updating scenario."""

    name: Optional[str] = None
    development_cost: Optional[float] = None
    holding_period_months: Optional[int] = None
    finance_type: Optional[str] = None
    finance_rate: Optional[float] = None
    assumptions: Optional[str] = None


class ScenarioResponse(ScenarioBase):
    """Schema for scenario response."""

    id: str
    property_id: str
    breakdown: Optional[ScenarioBreakdown] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SEARCH SCHEMAS
# ============================================================================


class SearchFilters(BaseModel):
    """Filters for property search."""

    postcode: str
    strategy: str
    radius: int = 1000  # meters


class SearchResponse(BaseModel):
    """Response for search endpoint."""

    properties: list[PropertyResponse]
    scores: dict[str, OpportunityScoreResponse]
    total: int
    offset: int = 0


# ============================================================================
# EXPORT SCHEMAS
# ============================================================================


class ExportOptions(BaseModel):
    """Options for exporting analysis."""

    include_scoring: bool = True
    include_precedents: bool = True
    include_scenarios: bool = True
    include_analysis: bool = True
    report_name: Optional[str] = None


class ExportResponse(BaseModel):
    """Response for export endpoint."""

    url: str
    format: str
    expires_in: int = 3600  # seconds
