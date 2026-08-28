"""Create a new attorney account (or update an existing one's password/email).

Usage:
    python scripts/create_attorney.py <username> [--email EMAIL] [--password PASSWORD]

Omit --password to be prompted instead (avoids it landing in shell history).
An attorney only receives lead-created notifications if --email is set.

Run from backend/ with the venv active and the local DB running.
"""

import argparse
import sys
from getpass import getpass

sys.path.insert(0, ".")

from app.db.session import SessionLocal
from app.models.attorney import Attorney
from app.services.auth import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("username")
    parser.add_argument("--email", default=None, help="Where lead notifications go")
    parser.add_argument("--password", default=None, help="Omit to be prompted instead")
    args = parser.parse_args()

    password = args.password or getpass("Password: ")

    db = SessionLocal()
    try:
        attorney = db.query(Attorney).filter(Attorney.username == args.username).first()
        if attorney is None:
            attorney = Attorney(
                username=args.username, password_hash=hash_password(password), email=args.email
            )
            db.add(attorney)
            action = "Created"
        else:
            attorney.password_hash = hash_password(password)
            if args.email is not None:
                attorney.email = args.email
            action = "Updated"
        db.commit()
        print(f"{action} attorney '{args.username}' (email: {attorney.email or 'none'}).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
