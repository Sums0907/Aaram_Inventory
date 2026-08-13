from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
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

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    # Connectors: ShopDeck
    SHOPDECK_BASE_URL: str = Field(default="https://pro.shopdeck.com")
    SHOPDECK_SESSION_COOKIE: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
