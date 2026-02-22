"""Opportunity scoring service - explainable scoring algorithm."""
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from app.services.planning_service import PlanningService
from app.types import Precedent, ScoreBreakdown, OpportunityScore


class ScoringService:
    """Service for calculating opportunity scores based on planning precedents."""

    def __init__(self):
        """Initialize scoring service."""
        self.planning_service = PlanningService()

    async def calculate_score(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 1000,
        strategy: Optional[str] = None,
    ) -> OpportunityScore:
        """
        Calculate opportunity score for a property.

        This is an explainable algorithm based on:
        1. Number and recency of nearby precedents
        2. Approval rate for similar applications
        3. Refusal patterns
        4. Density of approved schemes

        Args:
            latitude: Property latitude
            longitude: Property longitude
            radius_m: Analysis radius in meters
            strategy: Development strategy

        Returns:
            OpportunityScore with detailed breakdown
        """
        # Find nearby precedents
        precedents = await self.planning_service.search_nearby_precedents(
            latitude,
            longitude,
            radius_m,
            strategy,
        )

        # Analyze precedents
        analysis = self.planning_service.analyze_precedents(precedents)

        # Calculate component scores
        precedent_score = self._calculate_precedent_score(analysis, precedents)
        approval_score = self._calculate_approval_score(analysis)
        risk_score = self._calculate_risk_score(analysis, precedents)
        confidence_score = self._calculate_confidence_score(analysis, precedents)

        # Weighted total score
        total_score = (
            precedent_score * 0.40 +  # 40% weight
            approval_score * 0.35 +   # 35% weight
            (100 - risk_score) * 0.25  # 25% weight (inverse risk)
        )

        breakdown = ScoreBreakdown(
            precedents_found=analysis["total"],
            approved=analysis["approved"],
            refused=analysis["refused"],
            approval_rate=analysis["approval_rate"],
            nearby_schemes=len([p for p in precedents if p.distance_m < 500]),  # Within 500m
        )

        return OpportunityScore(
            property_id="",  # Will be set by caller
            score_total=round(total_score, 1),
            score_risk=round(risk_score, 1),
            score_confidence=round(confidence_score, 1),
            score_breakdown=breakdown,
        )

    def _calculate_precedent_score(self, analysis: dict, precedents: list[Precedent]) -> float:
        """
        Calculate precedent score based on quantity and recency.

        Score increases with more precedents, especially recent ones.
        """
        total = analysis["total"]

        # Base score: 0-60 based on precedent count (diminishing returns)
        if total == 0:
            return 0
        elif total < 3:
            base_score = total * 10
        elif total < 10:
            base_score = 30 + (total - 3) * 3
        else:
            base_score = 51 + min((total - 10) * 1, 9)

        # Recency boost: +10 if recent precedent (< 1 year)
        now = datetime.now()
        recent = [
            p for p in precedents
            if (now - datetime.fromisoformat(p.date_decided.split("T")[0])).days < 365
        ]
        if recent:
            base_score = min(base_score + 10, 70)

        return base_score

    def _calculate_approval_score(self, analysis: dict) -> float:
        """
        Calculate approval score based on historical approval rate.

        Higher approval rate = higher opportunity score.
        """
        approval_rate = analysis["approval_rate"]
        refused = analysis["refused"]

        # Core score from approval rate (0-80)
        approval_score = approval_rate * 80

        # Penalty for high refusal count (-5 per refusal)
        refusal_penalty = min(refused * 5, 20)

        return max(approval_score - refusal_penalty, 0)

    def _calculate_risk_score(self, analysis: dict, precedents: list[Precedent]) -> float:
        """
        Calculate risk score (0 = low risk, 100 = high risk).

        Risk factors:
        - High refusal rate
        - Withdrawn applications
        - No recent precedents
        """
        total = analysis["total"]

        if total == 0:
            return 70  # Unknown = high risk

        refusal_rate = analysis["refused"] / total if total > 0 else 0
        withdrawn_rate = analysis["withdrawn"] / total if total > 0 else 0

        # Base risk from refusals (40 points max)
        refusal_risk = refusal_rate * 40

        # Extra risk from withdrawals (20 points max)
        withdrawal_risk = withdrawn_rate * 20

        # Recency risk (-10 if recent)
        now = datetime.now()
        recent = [
            p for p in precedents
            if (now - datetime.fromisoformat(p.date_decided.split("T")[0])).days < 180
        ]
        recency_discount = 10 if recent else 0

        risk = refusal_risk + withdrawal_risk - recency_discount
        return min(max(risk, 10), 100)

    def _calculate_confidence_score(
        self,
        analysis: dict,
        precedents: list[Precedent],
    ) -> float:
        """
        Calculate confidence score (how confident are we in our assessment).

        Confidence increases with:
        - More precedents
        - Consistent decision patterns
        - Recent data
        """
        total = analysis["total"]
        approval_rate = analysis["approval_rate"]

        # Base on sample size (0-40)
        if total == 0:
            size_score = 0
        elif total < 5:
            size_score = total * 5
        else:
            size_score = 25 + min((total - 5) * 2, 15)

        # Consistency bonus: if approval rate is >70% or <30% (0-30)
        consistency = abs(approval_rate - 0.5) * 60  # 0-60, centered at 50%
        consistency_score = min(consistency, 30)

        # Recency bonus (0-30)
        now = datetime.now()
        recent = [
            p for p in precedents
            if (now - datetime.fromisoformat(p.date_decided.split("T")[0])).days < 365
        ]
        recency_score = len(recent) / max(total, 1) * 30

        confidence = size_score + consistency_score + recency_score
        return min(confidence, 100)


# Singleton instance
_scoring_service: Optional[ScoringService] = None


def get_scoring_service() -> ScoringService:
    """Get or create scoring service singleton."""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = ScoringService()
    return _scoring_service
