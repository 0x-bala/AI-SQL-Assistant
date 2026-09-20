import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "AI SQL Assistant"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DB_ENGINE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///./ai_sql_assistant.db"

    QUERY_TIMEOUT_SECONDS: float = 5.0
    MAX_QUERY_LIMIT: int = 100

    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
