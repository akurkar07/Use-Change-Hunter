"""Planning precedent analysis service."""
from typing import Optional

from loguru import logger

from app.clients.ibex_client import get_ibex_client
from app.services.cache_service import get_cache_service
from app.types import Precedent


class PlanningService:
    """Service for analyzing planning precedents."""

    def __init__(self):
        """Initialize planning service."""
        self.ibex_client = get_ibex_client()
        self.cache_service = get_cache_service()

    async def search_nearby_precedents(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 1000,
        strategy: Optional[str] = None,
    ) -> list[Precedent]:
        """
        Search for nearby planning precedents.

        Args:
            latitude: Search center latitude
            longitude: Search center longitude
            radius_m: Search radius in meters
            strategy: Developer strategy to filter by

        Returns:
            List of nearby precedents
        """
        # Generate cache key
        cache_key = self.ibex_client.generate_cache_key(
            latitude,
            longitude,
            radius_m,
            strategy,
        )

        # Try to get from cache
        cached_result = await self.cache_service.get_cached(cache_key)
        if cached_result:
            logger.info(f"Using cached precedents for {strategy} at ({latitude}, {longitude})")
            precedents = [Precedent(**p) for p in cached_result]
            return precedents

        # Fetch from Ibex API
        logger.info(f"Fetching precedents from Ibex API at ({latitude}, {longitude})")
        precedents = await self.ibex_client.search_planning_applications(
            latitude,
            longitude,
            radius_m,
            strategy,
        )

        # Cache the result (2 hour TTL for planning data)
        if precedents:
            cache_data = [p.dict() for p in precedents]
            await self.cache_service.set_cached(cache_key, {"precedents": cache_data}, ttl=7200)

        return precedents

    def analyze_precedents(
        self,
        precedents: list[Precedent],
    ) -> dict:
        """
        Analyze precedents to extract statistics.

        Args:
            precedents: List of precedents to analyze

        Returns:
            Dictionary with analysis results
        """
        approved = [p for p in precedents if p.decision == "approved"]
        refused = [p for p in precedents if p.decision == "refused"]
        withdrawn = [p for p in precedents if p.decision == "withdrawn"]

        total = len(precedents)
        approval_rate = len(approved) / total if total > 0 else 0

        return {
            "total": total,
            "approved": len(approved),
            "refused": len(refused),
            "withdrawn": len(withdrawn),
            "approval_rate": approval_rate,
            "average_distance_m": sum(p.distance_m for p in precedents) / total if total > 0 else 0,
        }

    def rank_precedents(
        self,
        precedents: list[Precedent],
        by_recency: bool = True,
    ) -> list[Precedent]:
        """
        Rank precedents by relevance.

        Args:
            precedents: List to rank
            by_recency: Sort by date if True

        Returns:
            Sorted precedents
        """
        if by_recency:
            return sorted(
                precedents,
                key=lambda p: p.date_decided,
                reverse=True,
            )
        else:
            return sorted(
                precedents,
                key=lambda p: p.distance_m,
            )


# Singleton instance
_planning_service: Optional[PlanningService] = None


def get_planning_service() -> PlanningService:
    """Get or create planning service singleton."""
    global _planning_service
    if _planning_service is None:
        _planning_service = PlanningService()
    return _planning_service
