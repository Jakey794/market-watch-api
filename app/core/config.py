from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "market-watch-api"
    app_env: str = "dev"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    postgres_db: str = "market_watch"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_port: int = 5432

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/market_watch"

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        allowed_values = {"dev", "test", "prod"}
        if value not in allowed_values:
            raise ValueError(f"app_env must be one of {sorted(allowed_values)}")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
