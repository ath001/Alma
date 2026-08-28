# Changelog

## Unreleased

- Initial project scaffold and Claude Code settings.
- Add `main.py` as a quick Python entry point to test the setup.
- Add `README.md` pointing to the GitHub repo.
- Add a local Postgres setup via `pg0-embedded` (`scripts/run_db.py` / `scripts/stop_db.py`, `requirements.txt`) — no existing DB was found on the machine, so this runs a self-contained, no-install/no-Docker Postgres for local dev, replaceable with a production DB later.
