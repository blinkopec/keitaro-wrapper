from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Keitaro Wrapper"
    API_V1_STR: str = "/api/v1"

    KEITARO_API_URL: str = ""
    KEITARO_API_KEY: str = ""

    KEITARO_DEFAULT_DOMAIN_ID: int = 0
    KEITARO_DEFAULT_GROUP_ID: int = 0
    KEITARO_DEFAULT_SOURCE_ID: int = 0

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
