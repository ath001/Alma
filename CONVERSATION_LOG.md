# Conversation Log

A running summary of Claude Code sessions in this repo — what was asked, what was done, and any decisions made. Not a full transcript; keep entries brief.

## 2026-08-28

- Created [main.py](main.py) as a placeholder Python entry point to test the setup (prints a greeting). Logged in CHANGELOG.md.
- Wrote the initial [CLAUDE.md](CLAUDE.md): noted the repo is currently just a scaffold, and that project.txt (then named Requirements.txt) is actually the product/tech assignment (not a pip file) — a lead-intake app using FastAPI + Next.js, public lead form, email notifications, auth-guarded internal UI, PENDING → REACHED_OUT lead states. Architecture (DB, email provider, auth) is still undecided.
- Started this conversation log at the user's request.
- Renamed `Requirements.txt` to [project.txt](project.txt) (its content was never a pip requirements file, so the old name was misleading) and updated references in CLAUDE.md.
- Amended the initial commit (already pushed to origin/main) to include all the above changes, per user confirmation, and force-pushed to sync origin/main.
- Added [README.md](README.md) pointing to the GitHub repo (https://github.com/ath001/Alma).
- Checked the machine for an existing local database (services, listening ports, Program Files, Docker, CLI tools) — found none. User chose Postgres, then specifically an embedded/no-install option over Docker or SQLite. `pgserver` (the initially known package) has no Windows distribution; found and used `pg0-embedded` instead, which does. Added `requirements.txt`, `scripts/run_db.py` (start, configurable `--port`, data in gitignored `.pg0data/`), `scripts/stop_db.py` (force-stop fallback), and a project-local `.venv/`. Hit and fixed a real bug: a forcefully-terminated `run_db.py` left orphaned `postgres.exe` processes because the shutdown path only ran on a clean `KeyboardInterrupt`; added a `SIGTERM` handler so termination also triggers `pg.stop()` via the `finally` block, and documented `stop_db.py` as the manual cleanup path. Documented usage in CLAUDE.md and README.md.
