from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, JSON, CheckConstraint, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class StrategyType(enum.Enum):
    """Scoring strategy types"""
    opportunity = "opportunity"
    risk = "risk"
    development = "development"
    sustainability = "sustainability"


class IbexCache(Base):
    """Cached IBEX API responses to protect credits"""
    __tablename__ = "ibex_cache"
    
    cache_key = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    payload_json = Column(JSONB, nullable=False)
    response_json = Column(JSONB, nullable=False)
    
    __table_args__ = (
        Index("ibex_cache_expires_at_idx", "expires_at"),
        Index("ibex_cache_created_at_idx", "created_at"),
    )


class Property(Base):
    """Real properties (points or inferred from planning sites)"""
    __tablename__ = "properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    property_type = Column(String, nullable=True)
    geom = Column(String, nullable=True)  # PostGIS GEOGRAPHY type stored as WKT
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("properties_postcode_idx", "postcode"),
    )


class OpportunityScore(Base):
    """Scoring results per strategy"""
    __tablename__ = "opportunity_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    strategy_type = Column(Enum(StrategyType), nullable=False)
    score_total = Column(Integer, nullable=False)
    score_risk = Column(Integer, nullable=False)
    score_confidence = Column(Integer, nullable=False)
    breakdown = Column(JSONB, nullable=False)
    scenario = Column(JSONB, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint("score_total >= 0 AND score_total <= 100"),
        CheckConstraint("score_risk >= 0 AND score_risk <= 100"),
        CheckConstraint("score_confidence >= 0 AND score_confidence <= 100"),
        Index("opportunity_scores_property_strategy_idx", "property_id", "strategy_type"),
        Index("opportunity_scores_generated_at_idx", "generated_at"),
    )


class Scenario(Base):
    """Planning scenarios for what-if analysis"""
    __tablename__ = "scenarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    scenario_type = Column(String, nullable=False)  # e.g., "extension", "hmo", "conversion"
    parameters = Column(JSONB, nullable=False)  # Custom parameters for the scenario
    results = Column(JSONB, nullable=True)  # Results from IBEX or analysis
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("scenarios_property_idx", "property_id"),
        Index("scenarios_scenario_type_idx", "scenario_type"),
    )
