"""Main API router."""
from fastapi import APIRouter

from app.api.routes import health, search, properties, scores, scenarios, export

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(scores.router, prefix="/scores", tags=["scores"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
