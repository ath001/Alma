import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import EmailStr

from app.api.deps import CurrentAttorney, DbSession
from app.config import get_settings
from app.models.lead import Lead, LeadState
from app.schemas.lead import LeadRead, lead_to_read
from app.services.notifications import notify_lead_created
from app.services.storage import StorageBackend, get_storage_backend

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    db: DbSession,
    storage: Annotated[StorageBackend, Depends(get_storage_backend)],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    resume: Annotated[UploadFile, File()],
) -> LeadRead:
    settings = get_settings()

    if resume.content_type not in settings.resume_allowed_content_types:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported resume file type")

    content = await resume.read()
    max_bytes = settings.resume_max_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Resume file too large")

    lead = Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_filename=resume.filename or "resume",
        resume_content_type=resume.content_type,
        resume_storage_key="",
    )
    lead.resume_storage_key = storage.save(
        lead_id=lead.id,
        filename=lead.resume_filename,
        content_type=lead.resume_content_type,
        content=content,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Out of scope for now — see app/services/notifications.py.
    notify_lead_created(lead)

    return lead_to_read(lead)


@router.get("", response_model=list[LeadRead])
def list_leads(db: DbSession, current_attorney: CurrentAttorney) -> list[LeadRead]:
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return [lead_to_read(lead) for lead in leads]


@router.post("/{lead_id}/reach-out", response_model=LeadRead)
def mark_reached_out(lead_id: uuid.UUID, db: DbSession, current_attorney: CurrentAttorney) -> LeadRead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lead not found")
    if lead.state != LeadState.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Lead is not in PENDING state")

    lead.state = LeadState.REACHED_OUT
    lead.reached_out_at = datetime.now(UTC)
    db.commit()
    db.refresh(lead)
    return lead_to_read(lead)


@router.get("/{lead_id}/resume")
def download_resume(
    lead_id: uuid.UUID,
    db: DbSession,
    current_attorney: CurrentAttorney,
    storage: Annotated[StorageBackend, Depends(get_storage_backend)],
) -> Response:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lead not found")

    content = storage.load(lead.resume_storage_key)
    return Response(
        content=content,
        media_type=lead.resume_content_type,
        headers={"Content-Disposition": f'attachment; filename="{lead.resume_filename}"'},
    )
