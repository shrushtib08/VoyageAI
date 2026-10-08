import getpass
import re
import sys

from pydantic import TypeAdapter, ValidationError
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.migrations import upgrade_legacy_columns
from app.database.session import Base, SessionLocal, engine
import app.models  # Register model metadata before creating tables.
from app.models.user import User


def create_admin(db: Session, email: str, username: str, password: str) -> User:
    if len(password) < 12 or len(password.encode("utf-8")) > 72:
        raise ValueError("Administrator passwords must be 12 to 72 UTF-8 bytes.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", username):
        raise ValueError("Username must be 3-50 letters, numbers, dots, underscores, or hyphens.")
    try:
        email = TypeAdapter(EmailStr).validate_python(email)
    except ValidationError as exc:
        raise ValueError("Enter a valid administrator email address.") from exc
    if db.query(User).filter((User.email == email) | (User.username == username)).first():
        raise ValueError("That email or username already exists; no account was changed.")

    user = User(
        email=email,
        username=username,
        full_name=username,
        hashed_password=hash_password(password),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> int:
    print("Create a VoyageAI administrator. Credentials are never printed or stored in plaintext.")
    email = input("Administrator email: ").strip()
    username = input("Administrator username: ").strip()
    password = getpass.getpass("Administrator password (12+ characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        return 1

    Base.metadata.create_all(bind=engine)
    upgrade_legacy_columns(engine)
    db = SessionLocal()
    try:
        user = create_admin(db, email, username, password)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        db.close()
    print(f"Administrator '{user.username}' created. Sign in at /admin/login.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
