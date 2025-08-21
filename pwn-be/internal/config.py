import os
from pydantic import BaseModel

class Settings(BaseModel):
    RUNNER_URL: str = os.getenv("RUNNER_URL", "http://127.0.0.1:8081")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "sqlite+aiosqlite:///./dev.db")

_settings = Settings()
def get_settings() -> Settings:
    return _settings