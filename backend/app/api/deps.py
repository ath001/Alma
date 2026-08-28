from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attorney import Attorney
from app.services.auth import get_attorney_for_token

DbSession = Annotated[Session, Depends(get_db)]

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_attorney(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> Attorney:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    attorney = get_attorney_for_token(db, credentials.credentials)
    if attorney is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    return attorney


CurrentAttorney = Annotated[Attorney, Depends(get_current_attorney)]


def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> str | None:
    return credentials.credentials if credentials else None


BearerToken = Annotated[str | None, Depends(get_bearer_token)]

__all__ = [
    "BearerToken",
    "CurrentAttorney",
    "DbSession",
    "get_bearer_token",
    "get_current_attorney",
    "get_db",
]
