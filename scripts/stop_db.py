"""Stop the local Postgres server started via run_db.py, in case it was left running
(e.g. after a forceful kill of run_db.py that skipped its normal shutdown).

Usage:
    python scripts/stop_db.py [--port 5432]
"""

import argparse
from pathlib import Path

from pg0 import Pg0

DATA_DIR = Path(__file__).resolve().parent.parent / ".pg0data"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5432, help="Port the server was started on (default: 5432)")
    args = parser.parse_args()

    Pg0(port=args.port, data_dir=str(DATA_DIR)).stop()
    print("Stopped (if it was running).")


if __name__ == "__main__":
    main()
