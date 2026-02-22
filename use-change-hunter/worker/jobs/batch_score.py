import os
from typing import List

import httpx
from celery import current_app as app
from loguru import logger


BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")


@app.task
def batch_score_properties(property_ids: List[str], strategy: str = "extension") -> dict:
    """Calculate scores for a batch of property IDs."""
    processed = 0
    failed = []

    with httpx.Client(timeout=30.0) as client:
        for property_id in property_ids:
            try:
                response = client.post(
                    f"{BACKEND_API_URL}/scores/{property_id}/calculate",
                    json={"strategy": strategy, "radius_m": 1200},
                )
                if response.status_code == 200:
                    processed += 1
                else:
                    failed.append(property_id)
                    logger.warning(
                        f"Score call failed for {property_id}: {response.status_code} {response.text}"
                    )
            except Exception as exc:
                failed.append(property_id)
                logger.warning(f"Score call error for {property_id}: {exc}")

    return {"processed": processed, "failed": failed, "strategy": strategy}
