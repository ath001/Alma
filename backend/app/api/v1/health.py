from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.health import DbHealthStatus, HealthStatus

router = APIRouter(tags=["health"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    return HealthStatus(status="ok")


@router.get("/health/db", response_model=DbHealthStatus)
def health_db(db: DbSession) -> DbHealthStatus:
    db.execute(text("SELECT 1"))
    return DbHealthStatus(status="ok", database="reachable")
