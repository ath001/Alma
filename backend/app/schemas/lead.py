import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.lead import Lead, LeadState


class LeadRead(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    resume_filename: str
    resume_url: str
    state: LeadState
    created_at: datetime
    updated_at: datetime
    reached_out_at: datetime | None


def lead_to_read(lead: Lead) -> LeadRead:
    return LeadRead(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        resume_filename=lead.resume_filename,
        resume_url=f"/api/v1/leads/{lead.id}/resume",
        state=lead.state,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        reached_out_at=lead.reached_out_at,
    )
