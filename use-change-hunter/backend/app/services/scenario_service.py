from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger


def model_financial_scenario(parameters: Dict[str, Any]) -> Dict[str, Any]:
    build_cost = float(parameters.get("build_cost", 0))
    contingency_pct = float(parameters.get("contingency_pct", 10))
    professional_fees_pct = float(parameters.get("professional_fees_pct", 8))
    finance_cost = float(parameters.get("finance_cost", 0))
    buy_price = float(parameters.get("buy_price", 0))
    stamp_legal = float(parameters.get("stamp_legal", 0))
    gdv = float(parameters.get("gdv", 0))
    annual_rent_uplift = float(parameters.get("annual_rent_uplift", 0))
    hold_years = float(parameters.get("hold_years", 1))
    risk_haircut_pct = float(parameters.get("risk_haircut_pct", 15))

    contingency = build_cost * contingency_pct / 100.0
    professional_fees = build_cost * professional_fees_pct / 100.0
    total_cost = buy_price + stamp_legal + build_cost + contingency + professional_fees + finance_cost
    gross_profit = gdv - total_cost
    rental_uplift_value = annual_rent_uplift * hold_years
    risk_adjusted_profit = gross_profit * (1.0 - (risk_haircut_pct / 100.0))

    return {
        "inputs": {
            "build_cost": build_cost,
            "contingency_pct": contingency_pct,
            "professional_fees_pct": professional_fees_pct,
            "finance_cost": finance_cost,
            "buy_price": buy_price,
            "stamp_legal": stamp_legal,
            "gdv": gdv,
            "annual_rent_uplift": annual_rent_uplift,
            "hold_years": hold_years,
            "risk_haircut_pct": risk_haircut_pct,
        },
        "outputs": {
            "contingency": round(contingency, 2),
            "professional_fees": round(professional_fees, 2),
            "total_cost": round(total_cost, 2),
            "gross_profit": round(gross_profit, 2),
            "rental_uplift_value": round(rental_uplift_value, 2),
            "risk_adjusted_profit": round(risk_adjusted_profit, 2),
            "gross_margin_pct": round((gross_profit / total_cost) * 100, 2) if total_cost > 0 else 0.0,
        },
        "explanation": [
            "Financial model uses explicit assumptions only.",
            "Risk-adjusted profit applies a simple haircut to gross profit.",
        ],
    }


async def create_scenario(
    property_id: str,
    db: AsyncSession,
    parameters: Dict[str, Any],
) -> Optional[dict]:
    logger.info(f"Creating scenario for property {property_id}")
    return model_financial_scenario(parameters)


async def compare_scenarios(
    property_id: str,
    db: AsyncSession,
    scenario_list: list,
) -> Optional[Dict[str, Any]]:
    logger.info(f"Comparing {len(scenario_list)} scenarios for property {property_id}")
    return {
        f"scenario_{idx}": model_financial_scenario(params)
        for idx, params in enumerate(scenario_list)
    }


async def optimize_scenario(
    property_id: str,
    db: AsyncSession,
    optimization_objective: str = "roi",
) -> Optional[dict]:
    logger.info(f"Optimizing scenario for property {property_id} (objective={optimization_objective})")
    return {
        "objective": optimization_objective,
        "message": "MVP optimizer not enabled yet; use compare_scenarios for explicit options.",
    }
