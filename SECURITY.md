# Security

## Reporting a vulnerability

This is a pre-production assignment repo. If you find a security issue, raise it with the repo owner directly rather than opening a public issue.

## Secrets and PII — never commit

Do not commit sensitive material to the repository, in code, config, tests, fixtures, or commit messages:

- **Secrets**: API keys, tokens, passwords, DB connection strings with real credentials, private keys (`.pem`/`.p12`), OAuth client secrets, email-provider keys (SES/SendGrid/Postmark/etc.), `.env` files.
  - Use `*.env.example` files with placeholder values. Keep real `backend/.env` and `frontend/.env.local` gitignored (they already are — see [.gitignore](.gitignore)).
  - Real secrets belong in the deployment environment or a secrets manager, never in `config.py` defaults or `*.env.example`.
- **PII**: real lead data — names, email addresses, phone numbers, uploaded resumes/CVs.
  - Tests and fixtures must use obviously-fake data (e.g. `Ada Lovelace`, `ada@example.com`).
  - Locally submitted leads live in `.pg0data/` (gitignored) — keep it that way.
  - Never drive state-mutating tests against whatever rows happen to be in the local DB; create disposable synthetic leads (see [DECISIONS.md](DECISIONS.md) debugging log).
- **Real credentials must never reach the test suite.** `backend/tests/conftest.py` has an autouse fixture that forces `SMTP_USERNAME`/`SMTP_PASSWORD` empty for every test, regardless of what's in a developer's local `backend/.env` — so filling in a real Gmail App Password for actual app usage can't cause `pytest` to send real emails through it. This matters generally: any credential added to `.env` for real usage needs a corresponding test-isolation check, not just a `.gitignore` entry.
- **Attorney passwords**: never log or print a plain-text password. `backend/scripts/create_attorney.py` accepts a password as a CLI arg for scripting convenience, but prefer omitting it (it'll prompt via `getpass`, hidden input) since CLI args land in shell history.

### Before every commit

Check the staged diff for the above:

```
git diff --cached
git diff --cached --name-only        # anything under a gitignored path? (.env, .pg0data/)
```

If something sensitive was already committed, tell the repo owner — rotating the secret and rewriting history is their call, not something to paper over with a follow-up commit.

### Known non-secrets (safe, do not "fix")

- `postgresql+psycopg://postgres:postgres@127.0.0.1:5432/postgres` appears in [backend/.env.example](backend/.env.example) and as the default in [backend/app/config.py](backend/app/config.py). This is the stock [pg0-embedded](https://pypi.org/project/pg0-embedded/) local default (`postgres`/`postgres` on loopback), not a real credential. The production `DATABASE_URL` must come from the environment.

### Last scan

Full repo scan (tracked files, working tree, all `.env` files, complete git history) on **2026-08-28**: no secrets or real PII found. Only the local-dev Postgres placeholder above, and synthetic test data.


## Current security posture (assignment-stage)

These are deliberate scope boundaries with seams in the code, not accidental holes — but they are real and must be closed before any real deployment. See [DECISIONS.md](DECISIONS.md) "Scope boundaries".

| Area | Status |
| --- | --- |
| Auth for `/internal` UI | Real session-cookie auth (`frontend/src/app/internal/layout.tsx` + `/login`). Passwords hashed with PBKDF2-HMAC-SHA256 (stdlib), never stored/logged in plain text. |
| Auth for `GET /api/v1/leads`, `POST /api/v1/leads/{id}/reach-out`, `GET /api/v1/leads/{id}/resume` | Requires a valid `Authorization: Bearer` session token (`app.api.deps.CurrentAttorney`). |
| Seeded `admin`/`admin` account | **Intentional placeholder, not a real credential to guard** — created by the first auth migration, but only when `SEED_DEV_ADMIN=true` (set for local dev/CI, unset by default). A real deployment running `alembic upgrade head` with this unset gets no such account; still, add real accounts via `backend/scripts/create_attorney.py` and disable/rotate the admin one before any real deployment if `SEED_DEV_ADMIN` was ever turned on there. |
| `POST /api/v1/leads` (public form) | Intentionally unauthenticated. Lead IDs are UUIDs so submission volume can't be inferred and resume URLs aren't guessable. |
| Session tokens | Opaque, `secrets.token_urlsafe(32)`, stored server-side in `attorney_sessions` with `expires_at` (default 1 week); `POST /api/v1/auth/logout` deletes the row (real invalidation, not just "the client forgets it"). |
| Session token transport | httpOnly cookie set by a Next.js Server Action, never exposed to browser JS; forwarded to the backend only by Next.js server-side code (Server Components/Actions, a Route Handler proxy for resume downloads) as `Authorization: Bearer`. |
| Resume upload validation | Content-type is client-supplied, not magic-byte sniffed — spoofable. Size capped (`resume_max_size_mb`, default 10). |
| CORS | Explicit allow-list from `Settings.cors_origins` (not `*`). |
| Transport | Local dev is plain HTTP. TLS is a deployment concern. |

## Dependency / CI checks

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs `ruff` + `pytest` (backend) and `lint` + `build` (frontend) on push and PR. There is no automated secret-scanning or dependency-audit step yet — consider adding `gitleaks` / `pip-audit` / `npm audit` when this moves toward production.
