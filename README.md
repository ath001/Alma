# Alma

GitHub: https://github.com/ath001/Alma

Lead intake app: a public form for prospects, an auth-guarded internal UI for attorneys. See [project.txt](project.txt) for the full assignment and [CLAUDE.md](CLAUDE.md) for repo guidance.

Monorepo: [backend/](backend/) (FastAPI) and [frontend/](frontend/) (Next.js), plus shared local-dev tooling at the root.

**Current state**: the three required pieces from [project.txt](project.txt) are all built — public lead intake with resume upload, email notifications, and an auth-guarded internal UI for attorneys to view leads and mark them reached out.

## Run the whole app locally

Three terminals, run in order (each stays open/running):

**1. Database** (from the repo root):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_db.py
```

**2. Backend** (new terminal):

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload --port 8010
```

Submitting a lead sends two emails (prospect + attorney) via SMTP — optional for local dev (skipped/logged if unconfigured). To actually send them, fill in `SMTP_USERNAME`/`SMTP_PASSWORD` in `backend/.env`; see [backend/README.md](backend/README.md#email) for the 2-minute Gmail App Password setup (no SES/SendGrid account needed).

**3. Frontend** (new terminal):

```
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Then open **http://localhost:3000** — you should see "Backend status: ok" and the lead-submission form. The internal leads list is at **http://localhost:3000/internal/leads**, guarded by a sign-in page — use the seeded dummy account **`admin` / `admin`** (see [backend/README.md](backend/README.md#auth) for adding real attorneys).

The backend defaults to port 8010 (not 8000) since 8000 is commonly taken by other local dev tools. If 8010 is taken too, run the backend with a different `--port` and update `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` to match before starting the frontend. If a port stays stuck ("address already in use") even after killing every process using it, it may be a lingering OS-level socket rather than a live process — check with `Get-NetTCPConnection -LocalPort <port>` + `Get-Process -Id <owningPid>` (PowerShell); if the PID resolves to no real process, a reboot usually clears it. Just use a different port in the meantime.

To stop: Ctrl+C each terminal (frontend, then backend), then Ctrl+C the DB terminal (or run `python scripts/stop_db.py` from the root if it's ever left running).

## Details

- [Local database](CLAUDE.md#local-database) — how it works, custom ports, resetting data.
- [backend/README.md](backend/README.md) — endpoints, tests, migrations.
- [frontend/README.md](frontend/README.md) — structure, what's stubbed vs. real.
