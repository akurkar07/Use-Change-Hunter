from typing import Optional, Tuple, Dict
import httpx
from loguru import logger

from app.core.config import settings


class GeocodeClient:
    """Client for geocoding services"""
    
    def __init__(self):
        self.api_key = settings.GEOCODE_API_KEY
        # Using OpenMapTiles or similar geocoding service (placeholder)
        self.base_url = "https://geocode.maps.co"
    
    async def geocode(self, address: str, postcode: Optional[str] = None) -> Optional[Dict]:
        """
        Convert address to geographic coordinates (latitude, longitude)
        
        Args:
            address: Street address
            postcode: Optional postcode for more accurate results
        
        Returns:
            Dict with lat/lon or None if geocoding failed
        """
        if not address:
            logger.warning("Empty address provided to geocode")
            return None
        
        try:
            query = address
            if postcode:
                query = f"{address}, {postcode}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={"q": query, "api_key": self.api_key},
                    timeout=10.0
                )
                
                response.raise_for_status()
                results = response.json()
                
                if not results:
                    logger.warning(f"No geocoding results for address: {address}")
                    return None
                
                first_result = results[0]
                return {
                    "lat": float(first_result.get("lat")),
                    "lon": float(first_result.get("lon")),
                    "address": first_result.get("display_name")
                }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Geocoding HTTP error: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Geocoding request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in geocoding: {e}")
            return None
    
    async def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert geographic coordinates to address
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Address string or None if reverse geocoding failed
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            logger.warning(f"Invalid coordinates provided: lat={lat}, lon={lon}")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/reverse",
                    params={"lat": lat, "lon": lon, "api_key": self.api_key},
                    timeout=10.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                return result.get("address", {}).get("display_name")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Reverse geocoding HTTP error: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Reverse geocoding request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in reverse geocoding: {e}")
            return None
