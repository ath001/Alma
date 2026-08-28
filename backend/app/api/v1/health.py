from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession
from app.schemas.health import DbHealthStatus, HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    return HealthStatus(status="ok")


@router.get("/health/db", response_model=DbHealthStatus)
def health_db(db: DbSession) -> DbHealthStatus:
    db.execute(text("SELECT 1"))
    return DbHealthStatus(status="ok", database="reachable")
