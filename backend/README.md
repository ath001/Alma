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
alembic upgrade head
uvicorn app.main:app --reload --port 8010
```

`alembic upgrade head` is required before the app is actually usable — it creates every table (`leads`, `attorneys`, etc.) and, via `SEED_DEV_ADMIN=true` (already set in `.env.example`), seeds the dummy `admin`/`admin` attorney account. Skipping it leaves the server running but every request that touches the DB fails with `relation "..." does not exist`.

Default port is 8010 (not the more commonly-taken 8000) to avoid clashing with other local dev tools.

- `GET /api/v1/health` — liveness check.
- `GET /api/v1/health/db` — proves DB connectivity (`SELECT 1` through the real session dependency).
- `POST /api/v1/leads` — create a lead. `multipart/form-data`: `first_name`, `last_name`, `email`, `resume` (file, PDF/DOC/DOCX/TXT, ≤10MB by default). Public, no auth (per spec). Returns `201`.
- `GET /api/v1/leads` — list all leads, newest first. **Requires an attorney session.**
- `POST /api/v1/leads/{id}/reach-out` — transitions a lead from `PENDING` to `REACHED_OUT`. **Requires an attorney session.** `404` if unknown, `409` if not currently `PENDING`.
- `GET /api/v1/leads/{id}/resume` — downloads the resume file. **Requires an attorney session.**

Resume files are stored in Postgres (`lead_resumes` table), not the filesystem — one piece of infra to run locally, and the blob commits atomically with the `Lead` row. Storage is behind a `StorageBackend` interface (`app/services/storage.py`); `Settings.resume_storage_backend` is the switch for moving to S3 later (currently only `"postgres"` is implemented — `"s3"` raises `NotImplementedError` as a marked seam).

### Auth

Two tables: `attorneys` (username + PBKDF2-HMAC-SHA256 password hash, stdlib `hashlib` — no new dependency) and `attorney_sessions` (opaque bearer token, `expires_at`, default TTL `Settings.session_ttl_hours` = 1 week). Protected endpoints depend on `CurrentAttorney` (`app/api/deps.py`), which reads `Authorization: Bearer <token>` and 401s if missing/invalid/expired.

- `POST /api/v1/auth/login` — `{username, password}` → `{token, username}`.
- `POST /api/v1/auth/logout` — invalidates the session server-side (not just "forget the token" client-side).
- `GET /api/v1/auth/me` — `{username}` if the token is valid, else `401`.

The first migration (`f3732c16dbe9_add_attorney_auth.py`) seeds one dummy account, **`admin` / `admin`**, using the real `hash_password()` function so it can never drift from the verify logic — but only when `SEED_DEV_ADMIN=true` (set in `.env.example`/local dev, and in CI). It's **off by default** so a real deployment can't get this account just by running `alembic upgrade head`; the seed is a no-op otherwise. This account is meant to be replaced/supplemented, not a permanent credential — add real attorneys with:

```
python scripts/create_attorney.py <username> <password>
```

(omit `<password>` to be prompted instead of passing it on the command line, which would otherwise land in shell history).

### Email

`app/services/notifications.py` emails the prospect a confirmation and the attorney a new-lead alert (with the resume filename and a "View lead" link to `{frontend_base_url}/internal/leads`), via plain SMTP (`smtplib`, stdlib — no new dependency). Both are `multipart/alternative` (plain text + HTML). If `SMTP_USERNAME`/`SMTP_PASSWORD` aren't set, sending is skipped (logged, not an error) — the app runs fine with no email configured.

To actually send: in `.env`, set `SMTP_USERNAME`/`SMTP_PASSWORD` to a Gmail account + an [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification enabled first — not your normal Gmail password), and `ATTORNEY_EMAIL` to wherever the internal alert should go — any address works, including a plus-addressed one on your own account (`you+attorney@gmail.com`) if you want a fake-but-checkable inbox. No SES/SendGrid/etc. account needed. If a test email doesn't show up, check Spam and search (not just browse) for the recipient address — Gmail's spam filtering can treat a plus-addressed variant differently even though delivery succeeds identically at the protocol level.

**Never enable `smtplib`'s `set_debuglevel(1)` (or similar raw protocol logging) while real credentials are configured** — it prints the base64-encoded `AUTH PLAIN` line, which trivially decodes back to the username and password.

## Tests

```
pytest
```

Runs against the real local Postgres (not SQLite), same as dev, to avoid dialect-mismatch bugs — so `alembic upgrade head` must have been run first (see Quickstart above).

## Migrations

```
alembic revision --autogenerate -m "..."
alembic upgrade head
```

`alembic/env.py` is wired to `app.config.Settings.database_url` and `app.models.Base.metadata` — no separate config needed.

Lead model/CRUD, email notifications, and attorney auth are done — see above.
