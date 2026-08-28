# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Monorepo with a FastAPI backend ([backend/](backend/)) and a Next.js frontend ([frontend/](frontend/)), each self-contained with their own dependency manifest and README. Current state: minimal but real, running skeletons only —

- **backend/**: `/api/v1/health` + `/api/v1/health/db`, and a working Lead feature — `POST /api/v1/leads` (create, multipart with resume upload), `GET /api/v1/leads` (list, deliberately unauthenticated for now), `POST /api/v1/leads/{id}/reach-out` (PENDING → REACHED_OUT), `GET /api/v1/leads/{id}/resume` (download). Resumes are stored in Postgres (`lead_resumes` table) behind a `StorageBackend` interface (`app/services/storage.py`) so switching to S3 later is one class + a setting flip, not a rewrite. Lead creation emails the prospect and the attorney via plain SMTP (`app/services/notifications.py`, stdlib `smtplib` — no SES/SendGrid needed); no-op (logged) if SMTP isn't configured. See [backend/README.md](backend/README.md).
- **frontend/**: real public lead-form (`/`) that submits to `POST /api/v1/leads` (loading/success/error states, `lib/api-client.ts`'s `createLead`), and a real internal leads list (`/internal/leads`) that renders `GET /api/v1/leads` as a table with a resume download link and a "Reach out" button (`internal/leads/actions.ts`, a Server Action calling `POST /api/v1/leads/{id}/reach-out` and revalidating the page) on `PENDING` rows — but **still unauthenticated**, same TODO in `internal/layout.tsx` as before. See [frontend/README.md](frontend/README.md).

**Not yet built**: real auth for `/internal` (and the matching backend endpoints), `docker-compose.yml`.

## What this project is meant to become

[project.txt](project.txt) contains the product/tech assignment this repo is meant to fulfill. Read it before starting substantial work. Summary:

- A "lead" intake app: a public form (first name, last name, email, resume/CV) for prospects.
- On submission, emails are sent to both the prospect and an attorney inside the company.
- An internal, auth-guarded UI lists leads with all submitted details.
- Each lead has a state: starts `PENDING`, transitions to `REACHED_OUT` when an attorney manually marks it after reaching out.
- Required stack: **FastAPI** for the API, **Next.js** for the web app, a persistence layer, and an email service integration.
- Code should be structured like a production-level repo (not a toy layout).

Architectural decisions still open: auth mechanism for `/internal`. Check with the user before committing to one if it isn't already specified elsewhere in the conversation.

## Local database

Postgres for local dev runs via [pg0-embedded](https://pypi.org/project/pg0-embedded/) — no system install or Docker needed; it downloads and manages real Postgres binaries itself. This is a dev/test convenience chosen because nothing else was installed on this machine at the time; a more production-representative setup (managed Postgres, Docker, etc.) is expected later.

- `pip install -r requirements.txt` (inside a venv, e.g. `.venv/`) to get `pg0-embedded`.
- `python scripts/run_db.py [--port 5432]` starts it in the foreground, printing the connection URI; Ctrl+C stops it cleanly. Data lives in `.pg0data/` (gitignored) — delete that folder to reset the DB.
- `python scripts/stop_db.py [--port 5432]` force-stops it if it was ever left running after a non-graceful kill of `run_db.py`.
- Default port is 5432; pass `--port` to both scripts together to run on another port if 5432 is already taken by something else.

## Secrets and PII

See [SECURITY.md](SECURITY.md). In short: never commit secrets (API keys, tokens, passwords, real connection strings, private keys, `.env` files) or real lead PII (names, emails, phone numbers, resumes), and check the staged diff before every commit.

## Changelog

Whenever you make a commit that changes code, add an entry to [CHANGELOG.md](CHANGELOG.md) in the same commit describing what changed and why.

## Conversation log

Keep [CONVERSATION_LOG.md](CONVERSATION_LOG.md) up to date: at the end of a session (or after a meaningful chunk of work), append a brief dated summary of what was asked and what was done. It's a summary log, not a full transcript — keep entries short.

## Decisions

[DECISIONS.md](DECISIONS.md) is the topical (not chronological) reference for *why* the codebase looks the way it does: key architectural decisions and their tradeoffs, real bugs found and fixed, and known limitations. When you make a non-obvious design choice, reject an alternative for a real reason, or hunt down a non-trivial bug, add it there — not just to CONVERSATION_LOG.md (which is the session narrative) or CHANGELOG.md (which is the what-changed list).
