"""Run a local, self-contained Postgres server for development.

No system install or Docker required — pg0-embedded downloads and manages
real Postgres binaries, storing data under .pg0data/ in the repo root.
Delete that folder to reset the database completely.

Usage:
    python scripts/run_db.py [--port 5432]
"""

import argparse
import signal
import sys
import time
from pathlib import Path

from pg0 import Pg0

DATA_DIR = Path(__file__).resolve().parent.parent / ".pg0data"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5432, help="Port to run Postgres on (default: 5432)")
    args = parser.parse_args()

    pg = Pg0(port=args.port, data_dir=str(DATA_DIR))
    pg.start()
    print(f"Postgres running at: {pg.uri}")
    print("Press Ctrl+C to stop.")

    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("Stopping Postgres...")
        pg.stop()


if __name__ == "__main__":
    main()
