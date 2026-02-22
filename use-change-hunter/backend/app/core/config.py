"""Core configuration for the Use-Change Hunter backend."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # FastAPI
    APP_NAME: str = "Use-Change Hunter API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_CREDENTIALS: bool = True

    # Database (support both individual params and DATABASE_URL)
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "use_change_hunter"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # External APIs
    IBEX_BASE_URL: str = "https://api.planningalerts.com"
    IBEX_JWT_TOKEN: Optional[str] = None  # From environment
    IBEX_CREDITS_THRESHOLD: int = 100  # Alert if credits fall below this

    # Geocoding
    GEOCODING_SERVICE: str = "nominatim"  # or other provider

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Get database URL, prefer DATABASE_URL env var, fallback to components."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Docker Compose style URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
