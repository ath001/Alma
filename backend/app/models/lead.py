import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, LargeBinary, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LeadState(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)

    # Opaque key into whichever StorageBackend saved the resume (see
    # app/services/storage.py) — not a DB foreign key, since the backend that
    # produced it may not be Postgres (e.g. an S3 object key).
    resume_storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_content_type: Mapped[str] = mapped_column(String(127), nullable=False)

    state: Mapped[LeadState] = mapped_column(
        Enum(LeadState, name="lead_state", native_enum=False, length=32),
        nullable=False,
        default=LeadState.PENDING,
        server_default=LeadState.PENDING.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    reached_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LeadResume(Base):
    """A minimal keyed blob store for resume bytes when resume_storage_backend
    is "postgres". All descriptive metadata (filename, content type) lives on
    Lead, not here — this table only exists to hold the bytes."""

    __tablename__ = "lead_resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
