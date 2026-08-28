import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings
from app.models.lead import Lead

logger = logging.getLogger(__name__)


def _send_email(*, to: str, subject: str, text_body: str, html_body: str) -> None:
    settings = get_settings()
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning("SMTP not configured; skipping email to %s (%s)", to, subject)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_address or settings.smtp_username
    message["To"] = to
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        if settings.smtp_use_tls:
            server.starttls()
            server.ehlo()
        if server.has_extn("auth"):
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


def _wrap_html(inner: str) -> str:
    return (
        '<div style="font-family: -apple-system, Segoe UI, Roboto, sans-serif; '
        'font-size: 15px; line-height: 1.5; color: #1a1a1a; max-width: 480px;">'
        f"{inner}"
        '<p style="margin-top: 32px; font-size: 13px; color: #6b7280;">Alma</p>'
        "</div>"
    )


def notify_lead_created(lead: Lead) -> None:
    """Emails the prospect a confirmation and the attorney a new-lead alert."""
    settings = get_settings()
    full_name = f"{lead.first_name} {lead.last_name}"

    _send_email(
        to=lead.email,
        subject=f"We've received your application, {lead.first_name}",
        text_body=(
            f"Hi {lead.first_name},\n\n"
            "Thanks for applying — we've received your information and resume.\n\n"
            "An attorney from our team will review your application and reach out "
            "with next steps soon.\n\n"
            "If you have any questions in the meantime, just reply to this email.\n\n"
            "— Alma"
        ),
        html_body=_wrap_html(
            f"<p>Hi {lead.first_name},</p>"
            "<p>Thanks for applying — we've received your information and resume.</p>"
            "<p>An attorney from our team will review your application and reach out "
            "with next steps soon.</p>"
            "<p>If you have any questions in the meantime, just reply to this email.</p>"
        ),
    )

    dashboard_url = f"{settings.frontend_base_url}/internal/leads"
    _send_email(
        to=settings.attorney_email,
        subject=f"New lead: {full_name}",
        text_body=(
            f"A new lead was submitted.\n\n"
            f"Name: {full_name}\n"
            f"Email: {lead.email}\n"
            f"Resume: {lead.resume_filename}\n"
            f"Submitted: {lead.created_at:%b %d, %Y at %I:%M %p UTC}\n\n"
            f"View and manage this lead: {dashboard_url}"
        ),
        html_body=_wrap_html(
            "<p>A new lead was submitted.</p>"
            '<table style="border-collapse: collapse;">'
            f'<tr><td style="padding: 2px 12px 2px 0; color: #6b7280;">Name</td><td>{full_name}</td></tr>'
            f'<tr><td style="padding: 2px 12px 2px 0; color: #6b7280;">Email</td><td>{lead.email}</td></tr>'
            f'<tr><td style="padding: 2px 12px 2px 0; color: #6b7280;">Resume</td><td>{lead.resume_filename}</td></tr>'
            f'<tr><td style="padding: 2px 12px 2px 0; color: #6b7280;">Submitted</td>'
            f"<td>{lead.created_at:%b %d, %Y at %I:%M %p UTC}</td></tr>"
            "</table>"
            f'<p style="margin-top: 20px;"><a href="{dashboard_url}" '
            'style="background: #111827; color: #fff; padding: 8px 16px; '
            'border-radius: 6px; text-decoration: none;">View lead</a></p>'
        ),
    )
