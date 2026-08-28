from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.health import DbHealthStatus, HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    return HealthStatus(status="ok")


@router.get("/health/db", response_model=DbHealthStatus)
def health_db(db: Session = Depends(get_db)) -> DbHealthStatus:
    db.execute(text("SELECT 1"))
    return DbHealthStatus(status="ok", database="reachable")
