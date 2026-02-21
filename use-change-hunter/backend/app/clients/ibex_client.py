from typing import Optional, Dict
import httpx
from loguru import logger

from app.core.config import settings


class IBEXClient:
    """Client for IBEX API integration (JWT authentication)"""
    
    def __init__(self):
        self.jwt_token = settings.IBEX_JWT
        self.base_url = settings.IBEX_BASE_URL
    
    async def post_search(self, payload: Dict) -> Optional[Dict]:
        """
        POST request to IBEX API for property analysis
        
        Args:
            payload: Request payload with property and analysis parameters
        
        Returns:
            API response or None if request failed
        """
        if not self.jwt_token:
            logger.error("IBEX JWT token not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.jwt_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    f"{self.base_url}/analyze",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                logger.info(f"IBEX API call successful: {response.status_code}")
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"IBEX API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"IBEX API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling IBEX API: {e}")
            return None
    
    async def search(self, query: str) -> Optional[Dict]:
        """
        Simple search query to IBEX API
        
        Args:
            query: Search query string
        
        Returns:
            Search results or None if request failed
        """
        payload = {"query": query}
        return await self.post_search(payload)
