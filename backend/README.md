# Alma backend

FastAPI app for lead intake. Structure: `app/api/v1` (routes), `app/models` (SQLAlchemy), `app/schemas` (Pydantic), `app/services` (business logic — storage, notifications), `app/db` (session/engine), `app/config.py` (settings). Migrations via Alembic in `alembic/`.

**Adding a new model?** Import it in `app/models/__init__.py` — `alembic/env.py` only sees tables reachable from that package import, so a model that's never imported there won't show up in `alembic revision --autogenerate`.

## Quickstart

Requires the local Postgres running first — see the root [README.md](../README.md#local-database).

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8010
```

Default port is 8010 (not the more commonly-taken 8000) to avoid clashing with other local dev tools.

- `GET /api/v1/health` — liveness check.
- `GET /api/v1/health/db` — proves DB connectivity (`SELECT 1` through the real session dependency).
- `POST /api/v1/leads` — create a lead. `multipart/form-data`: `first_name`, `last_name`, `email`, `resume` (file, PDF/DOC/DOCX/TXT, ≤10MB by default). Public, no auth (per spec). Returns `201`.
- `GET /api/v1/leads` — list all leads, newest first. **Unauthenticated for now** — real auth (attorney-only, per spec) isn't implemented yet; this is a known, deliberate gap, same as the frontend's `/internal` route.
- `POST /api/v1/leads/{id}/reach-out` — transitions a lead from `PENDING` to `REACHED_OUT`. `404` if unknown, `409` if not currently `PENDING`.
- `GET /api/v1/leads/{id}/resume` — downloads the resume file.

Resume files are stored in Postgres (`lead_resumes` table), not the filesystem — one piece of infra to run locally, and the blob commits atomically with the `Lead` row. Storage is behind a `StorageBackend` interface (`app/services/storage.py`); `Settings.resume_storage_backend` is the switch for moving to S3 later (currently only `"postgres"` is implemented — `"s3"` raises `NotImplementedError` as a marked seam).

### Email

`app/services/notifications.py` emails the prospect a confirmation and the attorney a new-lead alert (with the resume filename and a "View lead" link to `{frontend_base_url}/internal/leads`), via plain SMTP (`smtplib`, stdlib — no new dependency). Both are `multipart/alternative` (plain text + HTML). If `SMTP_USERNAME`/`SMTP_PASSWORD` aren't set, sending is skipped (logged, not an error) — the app runs fine with no email configured.

To actually send: in `.env`, set `SMTP_USERNAME`/`SMTP_PASSWORD` to a Gmail account + an [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification enabled first — not your normal Gmail password), and `ATTORNEY_EMAIL` to wherever the internal alert should go — any address works, including a plus-addressed one on your own account (`you+attorney@gmail.com`) if you want a fake-but-checkable inbox. No SES/SendGrid/etc. account needed. If a test email doesn't show up, check Spam and search (not just browse) for the recipient address — Gmail's spam filtering can treat a plus-addressed variant differently even though delivery succeeds identically at the protocol level.

**Never enable `smtplib`'s `set_debuglevel(1)` (or similar raw protocol logging) while real credentials are configured** — it prints the base64-encoded `AUTH PLAIN` line, which trivially decodes back to the username and password. See [SECURITY.md](../SECURITY.md) "Incidents".

## Tests

```
pytest
```

Runs against the real local Postgres (not SQLite), same as dev, to avoid dialect-mismatch bugs.

## Migrations

```
alembic revision --autogenerate -m "..."
alembic upgrade head
```

`alembic/env.py` is wired to `app.config.Settings.database_url` and `app.models.Base.metadata` — no separate config needed.

Real auth is not implemented yet. Lead model/CRUD and email notifications are done — see above.
