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

    # SMTP settings for the two lead-created notification emails: one to the
    # prospect, and one to every attorney that has an email set (Attorney.email
    # — see app/services/notifications.py). If smtp_username/smtp_password
    # are blank, sending is skipped (logged, not an error) — lets the app
    # run without email configured.
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_address: str = ""

    # Used to build the "view this lead" link in the attorney's email.
    frontend_base_url: str = "http://localhost:3000"

    # Attorney auth. Session tokens are opaque, stored in attorney_sessions,
    # sent as `Authorization: Bearer <token>`.
    session_ttl_hours: int = 24 * 7

    # Off by default so a real deployment can't accidentally get a dummy
    # admin/admin account just by running migrations — must be explicitly
    # opted into (local dev, CI). See the auth migration's upgrade().
    seed_dev_admin: bool = False
    # Email set on the seeded admin account when seed_dev_admin is true.
    # Placeholder by default — override in your local .env, never commit a
    # real address here.
    seed_dev_admin_email: str = "admin@example.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
