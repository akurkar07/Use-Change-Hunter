import os

import httpx
from celery import current_app as app
from loguru import logger


BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")
DEMO_QUERIES = ["EC1A 1BB", "SW1A 1AA", "M1 1AE", "B1 1AA"]
DEMO_STRATEGIES = ["extension", "hmo", "office_to_resi", "retail_to_mixed"]


@app.task
def prefetch_demo_data() -> dict:
    """Warm IBEX cache for demo areas and strategies."""
    success = 0
    failures = 0

    with httpx.Client(timeout=30.0) as client:
        for query in DEMO_QUERIES:
            for strategy in DEMO_STRATEGIES:
                try:
                    response = client.get(
                        f"{BACKEND_API_URL}/search",
                        params={"q": query, "strategy": strategy, "radius_m": 1200},
                    )
                    if response.status_code == 200:
                        success += 1
                    else:
                        failures += 1
                        logger.warning(
                            f"Prefetch failed for {query}/{strategy}: {response.status_code}"
                        )
                except Exception as exc:
                    failures += 1
                    logger.warning(f"Prefetch error for {query}/{strategy}: {exc}")

    return {"success": success, "failures": failures}
