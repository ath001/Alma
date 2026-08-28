import uuid
from typing import Protocol

from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.config import get_settings
from app.models.lead import LeadResume


class StorageBackend(Protocol):
    def save(self, *, lead_id: uuid.UUID, filename: str, content_type: str, content: bytes) -> str:
        """Persist bytes, return an opaque storage key to store on the Lead row."""
        ...

    def load(self, storage_key: str) -> bytes:
        """Retrieve the raw bytes for a previously-saved storage key."""
        ...


class PostgresStorage:
    """Keeps resume bytes in the lead_resumes table, in the same DB session
    as the Lead row that references them, so both commit atomically."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, *, lead_id: uuid.UUID, filename: str, content_type: str, content: bytes) -> str:
        blob = LeadResume(content=content)
        self.db.add(blob)
        self.db.flush()  # assign blob.id without committing the transaction
        return str(blob.id)

    def load(self, storage_key: str) -> bytes:
        blob = self.db.get(LeadResume, uuid.UUID(storage_key))
        if blob is None:
            raise FileNotFoundError(storage_key)
        return blob.content


def get_storage_backend(db: DbSession) -> StorageBackend:
    backend = get_settings().resume_storage_backend
    if backend == "postgres":
        return PostgresStorage(db)
    raise NotImplementedError(f"Resume storage backend {backend!r} is not implemented yet")
