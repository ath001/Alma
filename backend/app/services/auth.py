import base64
import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.attorney import Attorney, AttorneySession

_PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return base64.b64encode(salt + derived).decode()


def verify_password(password: str, password_hash: str) -> bool:
    raw = base64.b64decode(password_hash)
    salt, expected = raw[:16], raw[16:]
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return hmac.compare_digest(candidate, expected)


def authenticate(db: Session, *, username: str, password: str) -> Attorney | None:
    attorney = db.query(Attorney).filter(Attorney.username == username).first()
    if attorney is None or not verify_password(password, attorney.password_hash):
        return None
    return attorney


def create_session(db: Session, attorney: Attorney) -> AttorneySession:
    ttl = timedelta(hours=get_settings().session_ttl_hours)
    session = AttorneySession(
        token=secrets.token_urlsafe(32),
        attorney_id=attorney.id,
        expires_at=datetime.now(UTC) + ttl,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_attorney_for_token(db: Session, token: str) -> Attorney | None:
    session = db.get(AttorneySession, token)
    if session is None:
        return None
    if session.expires_at < datetime.now(UTC):
        return None
    return db.get(Attorney, session.attorney_id)


def invalidate_session(db: Session, token: str) -> None:
    session = db.get(AttorneySession, token)
    if session is not None:
        db.delete(session)
        db.commit()
