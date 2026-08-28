from datetime import UTC, datetime
from email.message import EmailMessage
from typing import ClassVar
from uuid import uuid4

from app.config import get_settings
from app.db.session import SessionLocal
from app.models.attorney import Attorney
from app.models.lead import Lead, LeadState
from app.services.auth import hash_password
from app.services.notifications import notify_lead_created


def _fake_lead() -> Lead:
    return Lead(
        id=uuid4(),
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        resume_storage_key="unused",
        resume_filename="resume.pdf",
        resume_content_type="application/pdf",
        state=LeadState.PENDING,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        reached_out_at=None,
    )


class _FakeSMTP:
    sent: ClassVar[list[EmailMessage]] = []

    def __init__(self, host, port):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def ehlo(self):
        pass

    def starttls(self):
        pass

    def has_extn(self, name):
        return True

    def login(self, username, password):
        pass

    def send_message(self, message):
        _FakeSMTP.sent.append(message)


def test_notify_lead_created_skips_silently_when_smtp_not_configured(monkeypatch, caplog):
    get_settings.cache_clear()
    db = SessionLocal()
    try:
        notify_lead_created(_fake_lead(), db)  # smtp_username/password default to ""
        assert "SMTP not configured" in caplog.text
    finally:
        db.close()
        get_settings.cache_clear()


def test_notify_lead_created_emails_prospect_and_every_attorney_with_email(monkeypatch):
    monkeypatch.setenv("SMTP_USERNAME", "sender@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password")
    get_settings.cache_clear()
    monkeypatch.setattr("app.services.notifications.smtplib.SMTP", _FakeSMTP)
    _FakeSMTP.sent = []

    db = SessionLocal()
    attorney_with_email = Attorney(
        username=f"notif-test-{uuid4().hex[:8]}",
        password_hash=hash_password("unused"),
        email="attorney+test@example.com",
    )
    attorney_without_email = Attorney(
        username=f"notif-test-noemail-{uuid4().hex[:8]}",
        password_hash=hash_password("unused"),
        email=None,
    )
    db.add_all([attorney_with_email, attorney_without_email])
    db.commit()

    try:
        notify_lead_created(_fake_lead(), db)
        by_recipient = {message["To"]: message for message in _FakeSMTP.sent}
        assert "ada@example.com" in by_recipient
        assert "attorney+test@example.com" in by_recipient

        prospect = by_recipient["ada@example.com"]
        assert "Ada" in prospect["Subject"]
        assert "Ada" in prospect.get_body(preferencelist=("plain",)).get_content()
        assert "Ada" in prospect.get_body(preferencelist=("html",)).get_content()

        attorney = by_recipient["attorney+test@example.com"]
        assert "Ada Lovelace" in attorney.get_body(preferencelist=("plain",)).get_content()
        html = attorney.get_body(preferencelist=("html",)).get_content()
        assert "resume.pdf" in html
        assert "/internal/leads" in html
    finally:
        db.delete(attorney_with_email)
        db.delete(attorney_without_email)
        db.commit()
        db.close()
        get_settings.cache_clear()
