"""Client for Ibex Planning Enterprise API."""
import hashlib
from datetime import datetime
from typing import Optional

import aiohttp
from loguru import logger

from app.core.config import get_settings
from app.types import Precedent

settings = get_settings()


class IbexClient:
    """Async client for Ibex planning API."""

    def __init__(self):
        """Initialize Ibex client."""
        self.base_url = settings.IBEX_BASE_URL
        self.jwt_token = settings.IBEX_JWT_TOKEN
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()

    async def search_planning_applications(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 1000,
        strategy: Optional[str] = None,
    ) -> list[Precedent]:
        """
        Search for planning applications near a location.

        Args:
            latitude: Latitude of search center
            longitude: Longitude of search center
            radius_m: Search radius in meters
            strategy: Filter by development strategy keyword

        Returns:
            List of planning precedents
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}

            params = {
                "lat": latitude,
                "lon": longitude,
                "radius": radius_m,
                "limit": 50,
            }

            async with self.session.get(
                f"{self.base_url}/api/planning/search",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    logger.error(f"Ibex API error: {response.status}")
                    return []

                data = await response.json()
                precedents = self._parse_applications(data.get("applications", []), strategy)
                logger.info(f"Found {len(precedents)} planning applications")
                return precedents

        except Exception as e:
            logger.error(f"Error fetching from Ibex API: {e}")
            return []

    def _parse_applications(
        self,
        applications: list[dict],
        strategy: Optional[str] = None,
    ) -> list[Precedent]:
        """Parse Ibex API response into Precedent objects."""
        precedents = []

        strategy_keywords = {
            "extension": ["extension", "rear", "side", "dormer"],
            "hmo": ["hmo", "house in multiple", "shared", "flat"],
            "office_residential": ["office", "residential", "conversion"],
            "retail_mixed": ["retail", "mixed", "commercial"],
            "flats": ["flat", "apartment", "conversion"],
        }

        for app in applications:
            try:
                proposal = app.get("description", "")
                decision = app.get("decision", "").lower()

                # Filter by strategy if provided
                if strategy and strategy in strategy_keywords:
                    keywords = strategy_keywords[strategy]
                    if not any(kw in proposal.lower() for kw in keywords):
                        continue

                precedent = Precedent(
                    reference=app.get("reference", ""),
                    proposal=proposal,
                    decision=decision if decision in ["approved", "refused", "withdrawn"] else "other",
                    date_decided=app.get("date_decided", ""),
                    distance_m=app.get("distance_m", 0),
                    lat=app.get("latitude", 0),
                    lng=app.get("longitude", 0),
                )
                precedents.append(precedent)

            except Exception as e:
                logger.warning(f"Error parsing application: {e}")
                continue

        return precedents

    def generate_cache_key(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        strategy: Optional[str] = None,
    ) -> str:
        """Generate deterministic cache key for search query."""
        key_parts = f"{latitude:.6f}:{longitude:.6f}:{radius_m}:{strategy or 'all'}"
        return hashlib.sha256(key_parts.encode()).hexdigest()


# Singleton instance
_ibex_client: Optional[IbexClient] = None


def get_ibex_client() -> IbexClient:
    """Get or create singleton Ibex client."""
    global _ibex_client
    if _ibex_client is None:
        _ibex_client = IbexClient()
    return _ibex_client
