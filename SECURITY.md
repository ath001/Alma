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
| Auth for `/internal` UI | **None.** TODO in `frontend/src/app/internal/layout.tsx`. |
| Auth for `GET /api/v1/leads` and `POST /api/v1/leads/{id}/reach-out` | **None.** Endpoints are publicly reachable. |
| `POST /api/v1/leads` (public form) | Intentionally unauthenticated. Lead IDs are UUIDs so submission volume can't be inferred and resume URLs aren't guessable. |
| Resume upload validation | Content-type is client-supplied, not magic-byte sniffed — spoofable. Size capped (`resume_max_size_mb`, default 10). |
| CORS | Explicit allow-list from `Settings.cors_origins` (not `*`). |
| Transport | Local dev is plain HTTP. TLS is a deployment concern. |

## Dependency / CI checks

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs `ruff` + `pytest` (backend) and `lint` + `build` (frontend) on push and PR. There is no automated secret-scanning or dependency-audit step yet — consider adding `gitleaks` / `pip-audit` / `npm audit` when this moves toward production.
