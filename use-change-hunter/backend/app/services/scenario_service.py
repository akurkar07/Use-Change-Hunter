"""Financial scenario modeling service."""
from typing import Optional

from loguru import logger

from app.schemas.schemas import ScenarioBreakdown


class ScenarioService:
    """Service for financial scenario modeling and analysis."""

    # Base assumptions for calculations
    PROPERTY_BASE_VALUE = 350000  # Default UK property value
    VALUE_UPLIFT_MULTIPLIER = 1.3  # 30% uplift from development
    LTV_RATIO = 0.7  # 70% loan to value
    SOFT_COSTS_RATIO = 0.15  # 15% of dev cost for soft costs

    def __init__(self):
        """Initialize scenario service."""
        pass

    def calculate_scenario_breakdown(
        self,
        development_cost: float,
        holding_period_months: int,
        finance_type: str = "cash",
        finance_rate: float = 0.0,
        property_value: float = PROPERTY_BASE_VALUE,
    ) -> ScenarioBreakdown:
        """
        Calculate financial breakdown for a development scenario.

        Args:
            development_cost: Estimated development cost in £
            holding_period_months: How long to hold the property
            finance_type: Type of financing (cash, btl_mortgage, development_loan)
            finance_rate: Annual interest rate (as decimal, e.g. 0.05 for 5%)
            property_value: Base property purchase value

        Returns:
            ScenarioBreakdown with detailed calculations
        """
        # Calculate ARV with value uplift
        estimated_uplift = development_cost * (self.VALUE_UPLIFT_MULTIPLIER - 1)
        estimated_arv = property_value + estimated_uplift

        # Calculate financing costs
        financing_cost = self._calculate_financing_cost(
            development_cost,
            holding_period_months,
            finance_type,
            finance_rate,
        )

        # Calculate soft costs
        soft_costs = development_cost * self.SOFT_COSTS_RATIO

        # Total costs
        total_cost = development_cost + financing_cost + soft_costs

        # Calculate profit
        estimated_profit = estimated_arv - property_value - total_cost

        # ROI percentage
        roi_percent = (estimated_profit / (property_value + development_cost)) * 100

        return ScenarioBreakdown(
            estimated_arv=round(estimated_arv, 2),
            estimated_cost=round(total_cost, 2),
            estimated_profit=round(estimated_profit, 2),
            roi_percent=round(roi_percent, 2),
            holding_months=holding_period_months,
            financing_cost=round(financing_cost, 2),
        )

    def _calculate_financing_cost(
        self,
        development_cost: float,
        holding_period_months: int,
        finance_type: str,
        finance_rate: float,
    ) -> float:
        """Calculate financing costs based on type and rate."""
        if finance_type == "cash":
            return 0  # No financing cost for cash

        # Calculate financed amount
        if finance_type == "btl_mortgage":
            # BTL: typically 70-75% LTV
            financed_amount = development_cost * 0.7
        elif finance_type == "development_loan":
            # Development loan: typically 60-70% of costs
            financed_amount = development_cost * 0.65
        else:
            financed_amount = development_cost * self.LTV_RATIO

        # Monthly interest calculation
        monthly_rate = finance_rate / 12
        monthly_interest = financed_amount * monthly_rate
        total_financing_cost = monthly_interest * holding_period_months

        return total_financing_cost

    def rank_scenarios(
        self,
        scenarios: list[dict],
        metric: str = "roi_percent",
    ) -> list[dict]:
        """
        Rank scenarios by a given metric.

        Args:
            scenarios: List of scenario dictionaries
            metric: Metric to rank by (roi_percent, estimated_profit, etc)

        Returns:
            Sorted scenarios
        """
        return sorted(
            scenarios,
            key=lambda s: s.get(metric, 0),
            reverse=True,
        )

    def compare_scenarios(
        self,
        scenarios: list[dict],
    ) -> dict:
        """
        Compare multiple scenarios and provide recommendation.

        Args:
            scenarios: List of scenario dictionaries

        Returns:
            Comparison analysis
        """
        if not scenarios:
            return {}

        highest_roi = max(scenarios, key=lambda s: s.get("roi_percent", 0))
        highest_profit = max(scenarios, key=lambda s: s.get("estimated_profit", 0))
        lowest_risk = min(scenarios, key=lambda s: s.get("estimated_cost", float("inf")))

        return {
            "best_roi": highest_roi,
            "best_profit": highest_profit,
            "lowest_cost": lowest_risk,
            "scenarios_count": len(scenarios),
            "average_roi": sum(s.get("roi_percent", 0) for s in scenarios) / len(scenarios),
        }

    def calculate_payback_period(
        self,
        estimated_profit: float,
        estimated_cost: float,
        monthly_cash_flow: float = 0,
    ) -> dict:
        """
        Calculate payback period for investment.

        Args:
            estimated_profit: Total estimated profit
            estimated_cost: Total development cost
            monthly_cash_flow: Monthly income during holding period

        Returns:
            Payback period analysis
        """
        if monthly_cash_flow <= 0:
            # No cash flow, payback is when property sells (at end of holding period)
            return {
                "payback_months": None,
                "payback_type": "upon_sale",
                "notes": "Returns realized upon sale",
            }

        monthly_net_return = monthly_cash_flow - (estimated_cost / 24)  # Amortize over 2 years
        if monthly_net_return <= 0:
            return {
                "payback_months": None,
                "payback_type": "negative",
                "notes": "Negative cash flow - not recommended",
            }

        payback_months = estimated_cost / monthly_net_return

        return {
            "payback_months": round(payback_months, 1),
            "payback_type": "ongoing",
            "notes": f"Breaks even in {round(payback_months, 1)} months",
        }


# Singleton instance
_scenario_service: Optional[ScenarioService] = None


def get_scenario_service() -> ScenarioService:
    """Get or create scenario service singleton."""
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioService()
    return _scenario_service
