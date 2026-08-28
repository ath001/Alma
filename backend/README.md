# Alma backend

FastAPI app for lead intake. Structure: `app/api/v1` (routes), `app/models` (SQLAlchemy), `app/schemas` (Pydantic), `app/services` (business logic, empty for now), `app/db` (session/engine), `app/config.py` (settings). Migrations via Alembic in `alembic/`.

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

`alembic/env.py` is wired to `app.config.Settings.database_url` and `app.models.base.Base.metadata` — no separate config needed.

Lead model/CRUD, email integration, and auth are not implemented yet.
