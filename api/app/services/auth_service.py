import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import (
    create_access_token,
    dummy_password_hash,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import RefreshToken, User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest

# House rule: age is the calendar date in Asia/Kolkata, not the host timezone.
KOLKATA = ZoneInfo("Asia/Kolkata")
_repo = UserRepository()


class UnderAgeError(Exception):
    def __init__(self) -> None:
        super().__init__("You must be 21 or older.")


class EmailTakenError(Exception):
    def __init__(self) -> None:
        super().__init__("Email already registered")


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Email or password is incorrect")


class InactiveUserError(Exception):
    def __init__(self) -> None:
        super().__init__("This account is inactive")


class InvalidRefreshError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid or expired session")


@dataclass
class SessionResult:
    user: User
    access_token: str
    refresh_token: str


def is_at_least_21(dob: date, today: date | None = None) -> bool:
    if today is None:
        today = datetime.now(KOLKATA).date()
    if dob > today:
        return False
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years >= 21


def register_user(db: Session, data: RegisterRequest) -> SessionResult:
    if not is_at_least_21(data.date_of_birth):
        raise UnderAgeError
    email = str(data.email).lower()
    if _repo.get_by_email(db, email) is not None:
        raise EmailTakenError
    user = User(
        email=email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=UserRole.customer,
        date_of_birth=data.date_of_birth,
        age_verified=True,
        is_active=True,
    )
    _repo.add_user(db, user)
    raw_refresh = _issue_refresh(db, user)
    _commit_or_email_taken(db)
    return _session(user, raw_refresh)


def login_user(db: Session, data: LoginRequest) -> SessionResult:
    email = str(data.email).lower()
    user = _repo.get_by_email(db, email)
    password_hash = user.password_hash if user is not None else dummy_password_hash()
    if user is None or not verify_password(data.password, password_hash):
        raise InvalidCredentialsError
    if not user.is_active:
        raise InactiveUserError
    raw_refresh = _issue_refresh(db, user)
    db.commit()
    return _session(user, raw_refresh)


def refresh_session(db: Session, raw_token: str | None) -> SessionResult:
    row = _usable_refresh(db, raw_token)
    row.revoked_at = datetime.now(timezone.utc)
    raw_refresh = _issue_refresh(db, row.user)
    db.commit()
    return _session(row.user, raw_refresh)


def logout_user(db: Session, raw_token: str | None) -> None:
    if not raw_token:
        return
    row = _repo.get_refresh_by_hash(db, hash_refresh_token(raw_token))
    if row is None or row.revoked_at is not None:
        return
    row.revoked_at = datetime.now(timezone.utc)
    db.commit()


def bootstrap_admin(db: Session, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    email = (settings.admin_email or "").strip().lower()
    if not email:
        return
    if "@" not in email or len(email) > 320:
        _halt("ADMIN_EMAIL is invalid. Refusing to start.")

    dob = _parse_admin_dob(settings.admin_date_of_birth)
    if dob is None:
        _halt("ADMIN_EMAIL is set but ADMIN_DATE_OF_BIRTH is missing or invalid. Refusing to start.")
    if not is_at_least_21(dob):
        _halt("ADMIN_DATE_OF_BIRTH is under 21 in Asia/Kolkata. Refusing to start.")

    password = settings.admin_password or ""
    if len(password) < 8:
        _halt("ADMIN_PASSWORD must be at least 8 characters. Refusing to start.")
    name = (settings.admin_name or "").strip()
    if not name or len(name) > 200:
        _halt("ADMIN_NAME is required (200 characters or fewer). Refusing to start.")

    existing = _repo.get_by_email(db, email)
    if existing is not None:
        return

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=name,
        phone=None,
        role=UserRole.admin,
        date_of_birth=dob,
        age_verified=True,
        is_active=True,
    )
    _repo.add_user(db, user)
    db.commit()
    print(f"Bootstrap admin ready for {email}", file=sys.stderr)


def _parse_admin_dob(raw: str | None) -> date | None:
    if raw is None or not raw.strip():
        return None
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        return None


def _halt(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def _issue_refresh(db: Session, user: User) -> str:
    settings = get_settings()
    raw = generate_refresh_token()
    token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    _repo.add_refresh(db, token)
    return raw


def _usable_refresh(db: Session, raw_token: str | None) -> RefreshToken:
    if not raw_token:
        raise InvalidRefreshError
    row = _repo.get_refresh_by_hash(db, hash_refresh_token(raw_token))
    now = datetime.now(timezone.utc)
    if row is None or row.revoked_at is not None or row.expires_at <= now:
        raise InvalidRefreshError
    if not row.user.is_active:
        raise InvalidRefreshError
    return row


def _session(user: User, raw_refresh: str) -> SessionResult:
    return SessionResult(user=user, access_token=create_access_token(user.id), refresh_token=raw_refresh)


def _commit_or_email_taken(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailTakenError from exc
