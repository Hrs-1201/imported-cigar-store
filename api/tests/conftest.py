import os
import re
from pathlib import Path

# Tests always use PostgreSQL. Set this before importing the app so the engine
# never points at the development database.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://ash:ash@127.0.0.1:5434/ash_cedar_test",
)
os.environ["JWT_SECRET"] = "test-secret-key-with-32-characters-min"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "14"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://127.0.0.1:3000"
os.environ["COOKIE_SECURE"] = "false"
os.environ["ADMIN_EMAIL"] = ""
os.environ["ADMIN_PASSWORD"] = ""
os.environ["ADMIN_NAME"] = ""
os.environ["ADMIN_DATE_OF_BIRTH"] = ""

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from app.core.db import SessionLocal
from app.main import app

API_ROOT = Path(__file__).resolve().parents[1]


def ensure_test_database() -> None:
    url = make_url(os.environ["DATABASE_URL"])
    name = url.database
    if not name or not re.fullmatch(r"[A-Za-z0-9_]+", name):
        raise RuntimeError(f"Refusing to create database {name!r}")
    admin_url = url.set(drivername="postgresql", database="postgres").render_as_string(hide_password=False)
    with psycopg.connect(admin_url, autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone()
        if exists is None:
            conn.execute(f'CREATE DATABASE "{name}"')


@pytest.fixture(scope="session", autouse=True)
def _migrate() -> None:
    ensure_test_database()
    command.upgrade(Config(str(API_ROOT / "alembic.ini")), "head")


@pytest.fixture(autouse=True)
def _clean_tables() -> None:
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        db.commit()
    finally:
        db.close()


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
