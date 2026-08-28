# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Monorepo with a FastAPI backend ([backend/](backend/)) and a Next.js frontend ([frontend/](frontend/)), each self-contained with their own dependency manifest and README. Current state: minimal but real, running skeletons only —

- **backend/**: `/api/v1/health` and `/api/v1/health/db` endpoints, DB session wired to the local Postgres, Alembic set up with zero real migrations, one pytest test. See [backend/README.md](backend/README.md).
- **frontend/**: placeholder public lead-form page (`/`, no submit logic yet) and placeholder auth-guarded internal leads list (`/internal/leads`, no real auth yet — TODO in `internal/layout.tsx`), with a live fetch of the backend's `/health` proving the cross-origin wiring works. See [frontend/README.md](frontend/README.md).

**Not yet built** (deliberately out of scope so far): the Lead model/schema/CRUD endpoints, email service integration, real auth for `/internal`, real form submission, `docker-compose.yml`. See the plan this structure was built from: `given-properly-structure-the-synthetic-rose.md` in the user's Claude plans directory, if it's still needed for reference.

## What this project is meant to become

[project.txt](project.txt) contains the product/tech assignment this repo is meant to fulfill. Read it before starting substantial work. Summary:

- A "lead" intake app: a public form (first name, last name, email, resume/CV) for prospects.
- On submission, emails are sent to both the prospect and an attorney inside the company.
- An internal, auth-guarded UI lists leads with all submitted details.
- Each lead has a state: starts `PENDING`, transitions to `REACHED_OUT` when an attorney manually marks it after reaching out.
- Required stack: **FastAPI** for the API, **Next.js** for the web app, a persistence layer, and an email service integration.
- Code should be structured like a production-level repo (not a toy layout).

Architectural decisions still open: email provider, auth mechanism for `/internal`. Check with the user before committing to one if it isn't already specified elsewhere in the conversation.

## Local database

Postgres for local dev runs via [pg0-embedded](https://pypi.org/project/pg0-embedded/) — no system install or Docker needed; it downloads and manages real Postgres binaries itself. This is a dev/test convenience chosen because nothing else was installed on this machine at the time; a more production-representative setup (managed Postgres, Docker, etc.) is expected later.

- `pip install -r requirements.txt` (inside a venv, e.g. `.venv/`) to get `pg0-embedded`.
- `python scripts/run_db.py [--port 5432]` starts it in the foreground, printing the connection URI; Ctrl+C stops it cleanly. Data lives in `.pg0data/` (gitignored) — delete that folder to reset the DB.
- `python scripts/stop_db.py [--port 5432]` force-stops it if it was ever left running after a non-graceful kill of `run_db.py`.
- Default port is 5432; pass `--port` to both scripts together to run on another port if 5432 is already taken by something else.

## Changelog

Whenever you make a commit that changes code, add an entry to [CHANGELOG.md](CHANGELOG.md) in the same commit describing what changed and why.

## Conversation log

Keep [CONVERSATION_LOG.md](CONVERSATION_LOG.md) up to date: at the end of a session (or after a meaningful chunk of work), append a brief dated summary of what was asked and what was done. It's a summary log, not a full transcript — keep entries short.
