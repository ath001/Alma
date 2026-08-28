# Decisions

A topical reference for *why* the codebase looks the way it does — key decisions, the tradeoffs behind them, and real bugs hit along the way. [CONVERSATION_LOG.md](CONVERSATION_LOG.md) is the chronological session-by-session record; this file is the distilled, organized version for someone trying to understand the current shape of things without reading the whole history.

## Local dev environment

- **Postgres via [pg0-embedded](https://pypi.org/project/pg0-embedded/)**, not Docker/SQLite/a native install. No DB was found on the machine at all (checked services, listening ports, Program Files, Docker, CLI tools). Chosen because it gives a *real* Postgres — same dialect/behavior as production — with zero setup (no installer, no Docker Desktop). `pgserver` was the first candidate but has no Windows distribution; `pg0-embedded` does. SQLite was rejected as the primary local DB because dialect differences can mask real bugs. `scripts/run_db.py` / `scripts/stop_db.py` wrap it; data lives in gitignored `.pg0data/`.
- **Backend default port is 8010, not 8000.** This dev machine already had something else (ComfyUI) bound to 8000; rather than just documenting a workaround, 8010 was made the permanent default everywhere so the conflict doesn't recur on other machines either.
- **Node.js wasn't installed at all** — installed via `winget install OpenJS.NodeJS.LTS` with explicit user approval before scaffolding the frontend.

## Repo structure

- **Monorepo**: top-level `backend/` (FastAPI) and `frontend/` (Next.js), each self-contained with its own dependency manifest and README, plus shared root-level dev tooling (the DB scripts). Chosen over two separate repos — simplest for a project this size; independent deploy/versioning wasn't a stated requirement.
- **Backend deps via `pyproject.toml`**, not `requirements.txt` — one file for both dependencies and tool config (ruff, pytest), the modern default for production FastAPI repos.
- **Frontend scaffolded with Tailwind** (`create-next-app --tailwind`) — fast to style the form/list, no reason to avoid it.
- **`docker-compose.yml` deferred**, not built yet — `project.txt` doesn't require Docker, and pg0-embedded already solves "no install needed" for local dev. Revisit when there's an actual deploy target.
- **`Requirements.txt` renamed to `project.txt`** — despite the name it was never a pip file, it's the product/tech assignment; the old name was actively misleading.

## Backend architecture

- **`/api/v1` prefix from the start** — avoids a URL restructure if there's ever a breaking v2.
- **DB access via a `DbSession = Annotated[Session, Depends(get_db)]` alias**, centralized in `app/api/deps.py`. (This pattern was actually started by the user/their IDE mid-session in `health.py`; adopted and centralized rather than reverting.) Never a module-level session or an inline `Depends()` default.
- **Explicit CORS allow-list** from `Settings.cors_origins` (default `http://localhost:3000`), not `allow_origins=["*"]`.
- **Alembic wired up from day one**, even before any real migration existed — establishes the autogenerate → review → upgrade pattern before there's anything real to migrate.
- **Backend tests run against the real local Postgres**, not SQLite or mocks — matches production dialect/behavior. Tradeoff: there's no per-test transaction-rollback fixture, so test runs leave real rows behind in the shared local DB (see Known limitations below).

## Lead feature design

- **Lead ID: UUID, not auto-increment int.** `POST /leads` is public and unauthenticated — sequential IDs would let anyone infer submission volume over time and made `/leads/{id}/resume` guessable for other prospects' files. UUID closes both at negligible cost.
- **State: SQLAlchemy `Enum(..., native_enum=False)`** (VARCHAR + CHECK), not a native Postgres enum type. Only two values today (`PENDING`, `REACHED_OUT`), but a future third state is realistic; a native PG enum needs `ALTER TYPE` surgery to extend, this just needs a constraint change.
- **Resume storage: kept in Postgres** (`lead_resumes` blob table, `bytea`), *not* the filesystem. The initial plan proposed local-filesystem storage (mirroring the "real, zero-setup, local-first" philosophy already used for the DB itself), but the user redirected: no second storage system to stand up for a dev-stage app when Postgres is already the only infra, and it's transactional — the blob and the `Lead` row commit together, so a crash mid-request can't orphan a file the way a filesystem write + separate DB commit could. Kept swappable: a `StorageBackend` Protocol (`app/services/storage.py`) plus a `resume_storage_backend` setting (`"postgres"` today, `"s3"` reserved and stubbed to raise `NotImplementedError`) — moving to S3 later is one class + a setting flip, not a rewrite of call sites.
- **Resume download via a dedicated `GET /leads/{id}/resume` endpoint**, not a static file mount. A mount can't validate the lead exists, can't set correct `Content-Type`/`Content-Disposition`, and can't be auth-gated later without changing the URL contract — the dynamic endpoint can do all three, and the URL shape stays stable even after swapping storage backends.
- **State transition via a dedicated `POST /leads/{id}/reach-out` action endpoint**, not a generic `PATCH /leads/{id}`. The only valid transition is one-directional and attorney-triggered; a generic PATCH would imply arbitrary field edits (renaming a prospect, changing their email) nothing asked for. `409 Conflict` if the lead isn't currently `PENDING`.
- **`resume_storage_key` is a plain string column, not a DB foreign key** — deliberately, so the column doesn't hardcode assumptions about which storage backend produced it (an S3 object key isn't a Postgres FK target).

## Scope boundaries (deliberate, not oversights)

Each of these has a TODO/seam in the code rather than being silently missing:
- **Email notifications** — `app/services/notifications.py::notify_lead_created()` is a no-op stub, called from the create endpoint so the seam is exercised. Provider (SES/SendGrid/Postmark/etc.) not chosen yet.
- **Auth for `/internal` and the corresponding backend endpoints** (`GET /leads`, `POST /leads/{id}/reach-out`) — both currently unauthenticated. Mechanism not chosen yet (NextAuth vs. backend-issued session vs. something else).
- **"Mark reached out" UI** — the backend endpoint exists and works; no button wired to it in the frontend yet.

## Debugging log

Real bugs found and fixed during this build (not exhaustive — see [CONVERSATION_LOG.md](CONVERSATION_LOG.md) for the full narrative):

- **Orphaned `postgres.exe` processes.** `run_db.py` only called `pg.stop()` on a clean `KeyboardInterrupt`; a forceful termination (SIGTERM) skipped the `finally` block entirely, leaving Postgres running in the background. Fixed with a `SIGTERM` handler that converts to `SystemExit` so cleanup always runs; `stop_db.py` added as a manual fallback for anything already orphaned.
- **Alembic autogenerate silently produces empty migrations for unregistered models.** `alembic/env.py` imported `app.models.base` (for `Base`), not `app.models` as a package — so a new model that's never imported anywhere never registers on `Base.metadata`, and autogenerate sees nothing. Fixed by importing every model in `app/models/__init__.py` and having `env.py` pull `Base` through that package import. **Convention going forward: any new model must be added to `app/models/__init__.py`.**
- **A running backend can silently serve stale code.** Restarted the server without `--reload` at one point; new endpoints returned `404` despite existing on disk, because the running process was importing the old module. Caught by checking the process's actual command line before assuming the code was broken.
- **No per-test DB isolation.** Backend tests hit the real local Postgres directly with no transaction-rollback fixture, so every `pytest` run leaves real rows behind. Not a correctness bug in the app, but required manually `TRUNCATE`-ing `leads`/`lead_resumes` several times during this session to hand back a clean DB. Flagged as a known limitation — see below.
- **Public form's submit button did nothing.** `handleSubmit` was a deliberate stub (`e.preventDefault()` only) left over from before the backend endpoint existed — caught by the user actually clicking it. Wired to the real `POST /api/v1/leads`.

### Environment/tooling quirks (not app bugs, but cost real debugging time)

- Sending `kill -TERM` through Git Bash/MSYS to a native Windows process doesn't reliably propagate — real interactive Ctrl+C works fine; this only affected scripted testing from this session, not actual usage.
- `source .venv/Scripts/activate && cmd &` backgrounds the whole compound command as one job in Git Bash, which forks a subshell — so the `source` doesn't activate the venv for *later* commands in the same script. Splitting into `source ...` on its own line first avoids it.
- `curl -F "resume=@C:/Windows/Temp/file.pdf"` failed (exit 26, "couldn't read file") from Git Bash; using a relative path in the repo's working directory worked. Environment-specific curl/path quirk.
- The auto-generated Alembic migration file failed `ruff check` (deprecated typing style, unsorted imports) — harmless boilerplate, fixed with `ruff check --fix`.
- `HTTP_413_REQUEST_ENTITY_TOO_LARGE` is deprecated in current Starlette/FastAPI — use `HTTP_413_CONTENT_TOO_LARGE`.
- `chromium-cli` (the usual tool for screenshotting a running dev server) isn't available in this Windows/Git-Bash environment. Fallback: install `playwright` ad hoc into a scratch directory (`npm install playwright && npx playwright install chromium`) and drive it with a small one-off Node script — not a project dependency, just a verification tool.

## Known limitations (flagged, not yet fixed)

- No per-test DB isolation/rollback fixture (see above) — real test-infra work, bigger than any single feature pass so far.
- `GET /api/v1/leads` has no pagination — fine at current scale, will need revisiting if lead volume grows.
- Resume content-type validation is client-supplied (`resume.content_type`), not magic-byte sniffed — spoofable, acceptable for now.
