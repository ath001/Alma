# Changelog

## Unreleased

- Initial project scaffold and Claude Code settings.
- Add `main.py` as a quick Python entry point to test the setup.
- Add `README.md` pointing to the GitHub repo.
- Add a local Postgres setup via `pg0-embedded` (`scripts/run_db.py` / `scripts/stop_db.py`, `requirements.txt`) — no existing DB was found on the machine, so this runs a self-contained, no-install/no-Docker Postgres for local dev, replaceable with a production DB later.
- Remove the placeholder `main.py` and restructure the repo into a monorepo: `backend/` (FastAPI skeleton with `/api/v1/health` + `/api/v1/health/db`, SQLAlchemy session, Alembic wired up, pytest) and `frontend/` (Next.js app-router skeleton with a placeholder public lead form and an auth-TODO'd internal leads list, both scaffolded with TypeScript + Tailwind). Verified end-to-end: backend tests pass against the real local Postgres, `next build`/`lint` pass, and the frontend's home page live-fetches backend `/health` successfully. Added `.github/workflows/ci.yml` (backend lint+test, frontend lint+build) and per-app READMEs. Installed Node.js LTS via winget (wasn't present on the machine).
- Rewrite the root `README.md` with a single "Run the whole app locally" quickstart (DB → backend → frontend, three terminals) so the full stack can be started end-to-end, including a note about the port-8000 conflict this dev machine has.
- Make port 8010 the documented default backend port (instead of uvicorn's built-in 8000) to avoid the common 8000 conflict going forward. Updated `frontend/src/lib/api-client.ts`'s fallback, `frontend/.env.local.example`, and the root/backend/frontend READMEs to match.
- Fix `ruff check` failures in the backend: sort/merge imports in `alembic/env.py` (I001), and move `health_db`'s `Depends(get_db)` out of the argument default into a module-level `DbSession = Annotated[...]` alias (B008).
