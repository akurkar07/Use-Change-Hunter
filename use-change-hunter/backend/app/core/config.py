from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import cached_property


class Settings(BaseSettings):
    # Postgres config (individual params for Docker compatibility)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "use_change_hunter"
    POSTGRES_USER: str = "uch"
    POSTGRES_PASSWORD: str = "uch"
    DATABASE_URL_OVERRIDE: str = Field(default="", alias="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Ibex API (uses JWT authentication)
    IBEX_BASE_URL: str = "https://api.ibexenterprise.com"
    IBEX_JWT: str = ""
    
    # Geocoding API
    GEOCODE_API_KEY: str = ""
    
    # API config
    API_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
    
    @cached_property
    def DATABASE_URL(self) -> str:
        """Build async PostgreSQL connection string"""
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE.replace("postgresql://", "postgresql+asyncpg://")
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
