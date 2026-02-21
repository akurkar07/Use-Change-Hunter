from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api import router

# Setup logging
setup_logging()

app = FastAPI(title="Use Change Hunter API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
