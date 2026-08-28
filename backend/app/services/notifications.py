from app.models.lead import Lead


def notify_lead_created(lead: Lead) -> None:
    """TODO: send a confirmation email to the prospect and a notification
    email to an attorney once an email service (e.g. SES/SendGrid/Postmark)
    is chosen. Intentionally a no-op for now."""
    return
