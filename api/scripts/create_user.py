"""Create or update a login. Safe in production (changes one user, deletes nothing).

    python scripts/create_user.py --username owner --full-name "U Kyaw Kyaw" --role owner
    python scripts/create_user.py --username sales1 --deactivate

The password is typed twice at a hidden prompt, never on the command line (it would show in `ps` and shell history).
Creating or updating a user with a new password also re-activates them.
"""
import argparse
import getpass
import sys
from pathlib import Path

import bcrypt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.models import User  # noqa: E402

MIN_LENGTH = 10


def ask_password() -> str:
    password = getpass.getpass("Password: ")
    if len(password) < MIN_LENGTH:
        sys.exit(f"Password must be at least {MIN_LENGTH} characters.")
    if len(password.encode()) > 72:
        sys.exit("Password must be at most 72 bytes (bcrypt limit).")
    if getpass.getpass("Password again: ") != password:
        sys.exit("Passwords do not match.")
    return password


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--username", required=True)
    parser.add_argument("--full-name")
    parser.add_argument("--role", choices=["owner", "sales"])
    parser.add_argument("--deactivate", action="store_true", help="disable the user's login; no password asked")
    args = parser.parse_args()

    with Session(create_engine(settings.database_url)) as db:
        user = db.scalars(select(User).where(User.username == args.username)).first()
        if args.deactivate:
            if user is None:
                sys.exit(f"No user {args.username!r}.")
            user.active = False
            db.commit()
            print(f"Deactivated {args.username}.")
            return
        if user is None and not (args.full_name and args.role):
            sys.exit("A new user needs --full-name and --role.")
        password_hash = bcrypt.hashpw(ask_password().encode(), bcrypt.gensalt()).decode()
        if user is None:
            user = User(username=args.username)
            db.add(user)
        user.full_name = args.full_name or user.full_name
        user.role = args.role or user.role
        user.password_hash = password_hash
        user.active = True
        print(f"{'Updated' if user.id else 'Created'} {args.username} ({user.role}).")
        db.commit()


if __name__ == "__main__":
    main()
