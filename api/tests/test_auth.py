from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

import jwt
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_refresh_token
from app.models.user import RefreshToken, User, UserRole
from app.services.auth_service import bootstrap_admin, is_at_least_21

KOLKATA = ZoneInfo("Asia/Kolkata")


def _email() -> str:
    return f"user-{uuid4()}@example.com"


def _shift_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, month=2, day=28)


def _register(client, **overrides):
    payload = {
        "full_name": "Asha Rao",
        "email": _email(),
        "phone": "9876543210",
        "password": "password123",
        "date_of_birth": "1990-04-12",
    }
    payload.update(overrides)
    return client.post("/api/v1/auth/register", json=payload)


def _count_users(db: Session) -> int:
    db.rollback()
    return int(db.scalar(select(func.count()).select_from(User)) or 0)


def _fetch_user(db: Session, email: str) -> User:
    db.rollback()
    user = db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


def test_age_boundary_calendar():
    assert is_at_least_21(date(2005, 11, 24), today=date(2026, 11, 24))
    assert not is_at_least_21(date(2005, 11, 25), today=date(2026, 11, 24))
    assert not is_at_least_21(date(2004, 2, 29), today=date(2025, 2, 28))
    assert is_at_least_21(date(2004, 2, 29), today=date(2025, 3, 1))


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_starts_session_for_adult(client, db_session):
    email = _email()
    response = _register(client, email=email, full_name="  Asha Rao  ")
    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == {"access_token", "token_type", "user"}
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    cookie = response.headers["set-cookie"]
    assert "refresh_token=" in cookie
    assert "HttpOnly" in cookie
    assert "Path=/" in cookie
    assert "samesite=lax" in cookie.lower()
    assert "Max-Age=1209600" in cookie
    assert set(body["user"]) == {"id", "email", "full_name", "phone", "role", "age_verified"}
    assert body["user"]["email"] == email
    assert body["user"]["full_name"] == "Asha Rao"
    assert body["user"]["phone"] == "9876543210"
    assert body["user"]["role"] == "customer"
    assert body["user"]["age_verified"] is True

    user = _fetch_user(db_session, email)
    raw_cookie = client.cookies.get("refresh_token")
    assert raw_cookie
    assert user.password_hash != "password123"
    assert user.password_hash.startswith("$argon2")
    stored = db_session.scalar(select(RefreshToken).where(RefreshToken.user_id == user.id))
    assert stored is not None
    assert stored.token_hash == hash_refresh_token(raw_cookie)
    assert stored.token_hash != raw_cookie

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email
    assert me.json()["role"] == "customer"

    payload = jwt.decode(body["access_token"], "test-secret-key-with-32-characters-min", algorithms=["HS256"])
    remaining = payload["exp"] - datetime.now(timezone.utc).timestamp()
    assert 14 * 60 <= remaining <= 15 * 60
    assert payload["type"] == "access"


def test_register_rejects_under_21_and_creates_no_user(client, db_session):
    email = _email()
    response = _register(client, email=email, date_of_birth="2015-01-01")
    assert response.status_code == 400
    assert response.json()["detail"] == "You must be 21 or older."
    assert "set-cookie" not in response.headers
    assert _count_users(db_session) == 0
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 401


def test_register_boundary_uses_kolkata_date(client):
    today = datetime.now(KOLKATA).date()
    adult = _register(client, date_of_birth=_shift_years(today, 21).isoformat())
    assert adult.status_code == 201, adult.text
    minor = _register(client, date_of_birth=(_shift_years(today, 21) + timedelta(days=1)).isoformat())
    assert minor.status_code == 400
    assert minor.json()["detail"] == "You must be 21 or older."


def test_register_duplicate_email_is_conflict(client):
    email = _email()
    assert _register(client, email=email).status_code == 201
    again = _register(client, email=email.upper(), full_name="Someone Else")
    assert again.status_code == 409
    assert again.json()["detail"] == "Email already registered"


def test_register_ignores_role_and_age_verified(client):
    response = _register(client, role="admin", age_verified=False)
    assert response.status_code == 201, response.text
    assert response.json()["user"]["role"] == "customer"
    assert response.json()["user"]["age_verified"] is True


def test_login_and_me(client):
    email = _email()
    assert _register(client, email=email).status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email.upper(), "password": "password123"})
    assert login.status_code == 200, login.text
    body = login.json()
    assert "refresh_token" not in body
    assert body["user"]["email"] == email
    assert "HttpOnly" in login.headers["set-cookie"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["full_name"] == "Asha Rao"


def test_login_invalid_credentials_are_indistinguishable(client):
    email = _email()
    assert _register(client, email=email).status_code == 201
    wrong = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})
    missing = client.post("/api/v1/auth/login", json={"email": _email(), "password": "password123"})
    assert wrong.status_code == 401
    assert missing.status_code == 401
    assert wrong.json() == missing.json()
    assert wrong.json()["detail"] == "Email or password is incorrect"


def test_inactive_user_is_forbidden(client, db_session):
    email = _email()
    assert _register(client, email=email).status_code == 201
    user = _fetch_user(db_session, email)
    user.is_active = False
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 403
    assert response.json()["detail"] == "This account is inactive"


def test_me_missing_or_expired_token_is_401(client):
    missing = client.get("/api/v1/auth/me")
    assert missing.status_code == 401
    assert missing.json()["detail"] == "Not authenticated"

    invalid = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert invalid.status_code == 401

    registered = _register(client)
    assert registered.status_code == 201
    user_id = registered.json()["user"]["id"]
    expired = jwt.encode(
        {
            "sub": user_id,
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        "test-secret-key-with-32-characters-min",
        algorithm="HS256",
    )
    stale = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert stale.status_code == 401
    assert stale.json()["detail"] == "Invalid or expired token"


def test_refresh_rotates_cookie_and_rejects_reuse(client, db_session):
    registered = _register(client)
    assert registered.status_code == 201
    original = client.cookies.get("refresh_token")
    assert original
    first_access = registered.json()["access_token"]

    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200, refreshed.text
    rotated = refreshed.json()
    assert "refresh_token" not in rotated
    assert rotated["access_token"]
    assert rotated["user"]["email"] == registered.json()["user"]["email"]
    new_cookie = client.cookies.get("refresh_token")
    assert new_cookie and new_cookie != original

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {rotated['access_token']}"})
    assert me.status_code == 200

    db_session.rollback()
    old_row = db_session.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(original)))
    assert old_row is not None
    assert old_row.revoked_at is not None

    client.cookies.set("refresh_token", original, path="/")
    reused = client.post("/api/v1/auth/refresh")
    assert reused.status_code == 401
    assert reused.json()["detail"] == "Invalid or expired session"

    client.cookies.set("refresh_token", new_cookie, path="/")
    still_valid = client.post("/api/v1/auth/refresh")
    assert still_valid.status_code == 200, still_valid.text
    assert first_access != still_valid.json()["access_token"]


def test_refresh_expired_token(client, db_session):
    assert _register(client).status_code == 201
    raw = client.cookies.get("refresh_token")
    stored = db_session.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw)))
    assert stored is not None
    stored.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


def test_logout_revokes_refresh_and_me_without_bearer_is_401(client):
    registered = _register(client)
    assert registered.status_code == 201
    access = registered.json()["access_token"]
    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert logout.content == b""

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 401
    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 401

    # The access JWT is stateless until it expires. The browser drops it on logout.
    still_signed = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert still_signed.status_code == 200


def test_logout_without_cookie_is_204(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204


def test_short_password_is_validation_error(client):
    response = _register(client, password="short")
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_bootstrap_admin_can_log_in(client, db_session):
    bootstrap_admin(
        db_session,
        Settings(
            admin_email="Admin@Example.com",
            admin_password="change-me-admin-password",
            admin_name="Store Admin",
            admin_date_of_birth="1990-01-01",
        ),
    )
    user = _fetch_user(db_session, "admin@example.com")
    assert user.role == UserRole.admin
    assert user.age_verified is True
    assert user.date_of_birth.isoformat() == "1990-01-01"
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "change-me-admin-password"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["role"] == "admin"


@pytest.mark.parametrize("dob", ["", "   ", "not-a-date", "2015-01-01"])
def test_bootstrap_bad_dob_exits_without_user(db_session, dob):
    with pytest.raises(SystemExit) as exc:
        bootstrap_admin(
            db_session,
            Settings(
                admin_email="admin@example.com",
                admin_password="change-me-admin-password",
                admin_name="Store Admin",
                admin_date_of_birth=dob,
            ),
        )
    assert exc.value.code == 1
    assert _count_users(db_session) == 0


def test_bootstrap_missing_password_exits_without_user(db_session):
    with pytest.raises(SystemExit) as exc:
        bootstrap_admin(
            db_session,
            Settings(
                admin_email="admin@example.com",
                admin_password="",
                admin_name="Store Admin",
                admin_date_of_birth="1990-01-01",
            ),
        )
    assert exc.value.code == 1
    assert _count_users(db_session) == 0


def test_bootstrap_does_not_change_existing_user(client, db_session):
    email = "admin@example.com"
    registered = _register(client, email=email, password="customer-password", date_of_birth="1990-04-12")
    assert registered.status_code == 201
    before = _fetch_user(db_session, email)
    password_hash = before.password_hash
    bootstrap_admin(
        db_session,
        Settings(
            admin_email=email,
            admin_password="change-me-admin-password",
            admin_name="Store Admin",
            admin_date_of_birth="1980-01-01",
        ),
    )
    after = _fetch_user(db_session, email)
    assert after.password_hash == password_hash
    assert after.role == UserRole.customer
    assert after.date_of_birth.isoformat() == "1990-04-12"
    assert after.full_name == "Asha Rao"
    assert _count_users(db_session) == 1
    original = client.post("/api/v1/auth/login", json={"email": email, "password": "customer-password"})
    assert original.status_code == 200
    assert original.json()["user"]["role"] == "customer"
    other = client.post("/api/v1/auth/login", json={"email": email, "password": "change-me-admin-password"})
    assert other.status_code == 401


def test_bootstrap_skips_when_email_unset(db_session):
    bootstrap_admin(
        db_session,
        Settings(
            admin_email="",
            admin_password="change-me-admin-password",
            admin_name="Store Admin",
            admin_date_of_birth="1990-01-01",
        ),
    )
    assert _count_users(db_session) == 0
