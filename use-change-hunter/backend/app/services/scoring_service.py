from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.services.planning_service import summarize_precedents


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def build_explainable_scores(summary: Dict[str, Any]) -> Dict[str, Any]:
    approved = summary.get("approved_similar", 0)
    refused = summary.get("refused_similar", 0)
    recent_approved = summary.get("recent_approved", 0)
    recent_refused = summary.get("recent_refused", 0)
    matched = summary.get("matched_precedents", 0)

    density_score = min(35.0, matched * 2.5)
    precedent_balance = (approved * 4.0) - (refused * 3.5)
    recency_bonus = (recent_approved * 4.5) - (recent_refused * 3.0)

    opportunity = _clamp_score(28.0 + density_score + precedent_balance + recency_bonus)
    risk = _clamp_score(65.0 - (approved * 3.0) + (refused * 4.0) - (recent_approved * 1.5))
    confidence = _clamp_score(
        min(40.0, matched * 3.0) + min(25.0, recent_approved * 4.0) + min(20.0, approved * 2.0)
    )

    explanation = [
        f"{approved} similar approvals and {refused} refusals in search radius",
        f"{recent_approved} recent approvals in last 24 months",
        f"{matched} total matched precedents for strategy",
    ]
    if recent_refused:
        explanation.append(f"{recent_refused} recent refusals increased risk")

    return {
        "score_total": opportunity,
        "score_risk": risk,
        "score_confidence": confidence,
        "breakdown": {
            **summary,
            "density_component": round(density_score, 2),
            "precedent_component": round(precedent_balance, 2),
            "recency_component": round(recency_bonus, 2),
            "explanation": explanation,
        },
    }


async def calculate_opportunity_score(
    property_id: str,
    db: AsyncSession,
    factors: Dict[str, Any] = None,
    strategy_type: str = "opportunity",
) -> Optional[dict]:
    """
    Calculate deterministic and explainable scores.

    `db` is retained in signature for compatibility with current call sites.
    """
    logger.info(f"Calculating {strategy_type} score for property {property_id}")

    if factors is None:
        factors = {}

    summary = factors.get("precedent_summary")
    if not summary:
        applications = factors.get("applications", [])
        summary = summarize_precedents(applications, factors.get("strategy", "extension"))

    scored = build_explainable_scores(summary)
    return {
        "property_id": property_id,
        "strategy_type": strategy_type,
        **scored,
    }


async def calculate_risk_score(
    property_id: str,
    db: AsyncSession,
    risk_model: str = "balanced",
) -> Optional[dict]:
    logger.info(f"Calculating risk score for property {property_id} (model={risk_model})")
    return await calculate_opportunity_score(
        property_id,
        db,
        factors={"strategy": "extension"},
        strategy_type="risk",
    )


async def calculate_sustainability_score(
    property_id: str,
    db: AsyncSession,
    include_carbon: bool = True,
) -> Optional[dict]:
    logger.info(f"Calculating sustainability score for property {property_id}")
    return await calculate_opportunity_score(
        property_id,
        db,
        factors={"strategy": "extension"},
        strategy_type="sustainability",
    )
