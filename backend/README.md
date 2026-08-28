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

Resume files are stored in Postgres (`lead_resumes` table), not the filesystem — one piece of infra to run locally, and the blob commits atomically with the `Lead` row. Storage is behind a `StorageBackend` interface (`app/services/storage.py`); `Settings.resume_storage_backend` is the switch for moving to S3 later (currently only `"postgres"` is implemented — `"s3"` raises `NotImplementedError` as a marked seam). Email notifications on lead creation are a no-op stub (`app/services/notifications.py`) — not implemented yet.

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

Email integration and real auth are not implemented yet. Lead model/CRUD is done — see above.
