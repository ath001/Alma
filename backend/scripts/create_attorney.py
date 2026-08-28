"""Create a new attorney account (or reset an existing one's password).

Usage:
    python scripts/create_attorney.py <username> <password>

Run from backend/ with the venv active and the local DB running.
"""

import sys
from getpass import getpass

sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.attorney import Attorney
from app.services.auth import hash_password


def main() -> None:
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        raise SystemExit(1)

    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) == 3 else getpass("Password: ")

    db = SessionLocal()
    try:
        attorney = db.query(Attorney).filter(Attorney.username == username).first()
        if attorney is None:
            attorney = Attorney(username=username, password_hash=hash_password(password))
            db.add(attorney)
            action = "Created"
        else:
            attorney.password_hash = hash_password(password)
            action = "Updated password for"
        db.commit()
        print(f"{action} attorney '{username}'.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
