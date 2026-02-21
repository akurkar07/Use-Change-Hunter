from fastapi import APIRouter

from app.api.routes import health, search, property, score, scenario, export

router = APIRouter()

# Include route modules
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(property.router, prefix="/properties", tags=["properties"])
router.include_router(score.router, prefix="/scores", tags=["scores"])
router.include_router(scenario.router, prefix="/scenarios", tags=["scenarios"])
router.include_router(export.router, prefix="/export", tags=["export"])
