from typing import Any
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = Field(default="AaramBooks API")
    APP_VERSION: str = Field(default="0.2.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    # Server Config
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database Config
    DATABASE_ENV: str = Field(default="development")
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/aarambooks")
    DATABASE_URL_SYNC: str = Field(default="postgresql://postgres:postgres@localhost:5432/aarambooks")
    DB_POOL_SIZE: int = Field(default=5)
    DB_MAX_OVERFLOW: int = Field(default=10)

    # Security
    SECRET_KEY: str = Field(default="super-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # AaramIdentity Consumer Integration
    AUTH_MODE: str = Field(default="local", description="Set to 'aaramidentity' for production RS256 token verification")
    AARAMIDENTITY_URL: str = Field(default="http://localhost:8001")
    IDENTITY_API_URL: str | None = Field(default=None)
    AARAMIDENTITY_PUBLIC_KEY: str | None = Field(default=None)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    # Connectors: ShopDeck
    SHOPDECK_BASE_URL: str = Field(default="https://pro.shopdeck.com")
    SHOPDECK_SESSION_COOKIE: str = Field(default="")
    SHOPDECK_SALES_WAREHOUSE_CODE: str = Field(default="WH-TEST")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if settings.ENVIRONMENT == "production" and settings.AUTH_MODE == "local":
        raise ValueError("AUTH_MODE='local' is forbidden in production. Must use 'aaramidentity'.")
        
    if not settings.IDENTITY_API_URL:
        import os
        legacy = os.getenv("IDENTITY_SERVICE_URL")
        settings.IDENTITY_API_URL = legacy or ("https://api-identity.aarambooks.cloud" if settings.ENVIRONMENT == "production" else "http://localhost:9000")
        
    import os
    if settings.SHOPDECK_SALES_WAREHOUSE_CODE and "SHOPDECK_SALES_WAREHOUSE_CODE" not in os.environ:
        os.environ["SHOPDECK_SALES_WAREHOUSE_CODE"] = settings.SHOPDECK_SALES_WAREHOUSE_CODE

    return settings
