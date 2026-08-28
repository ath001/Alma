# Alma

GitHub: https://github.com/ath001/Alma

See [project.txt](project.txt) for the project assignment and [CLAUDE.md](CLAUDE.md) for repo guidance.

## Local database

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_db.py        # starts Postgres locally, prints the connection URI
```

No system Postgres or Docker install needed — see [CLAUDE.md](CLAUDE.md#local-database) for details, including how to run on a different port or stop it.
