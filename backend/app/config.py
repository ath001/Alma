from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/postgres"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Where resume/CV uploads are persisted. "postgres" keeps bytes in the
    # lead_resumes table (see app/services/storage.py); "s3" is reserved for
    # when this needs to move off Postgres and is not implemented yet.
    resume_storage_backend: Literal["postgres", "s3"] = "postgres"
    resume_max_size_mb: int = 10
    resume_allowed_content_types: list[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
