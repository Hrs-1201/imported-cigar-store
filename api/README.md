# api

Backend for Ash & Cedar. This folder is a **separate project** from `web/`.

| | |
|--|--|
| Language | Python |
| Framework | FastAPI |
| Database | **PostgreSQL 16** — only this app connects to it |
| Access | SQLAlchemy + Alembic migrations |
| Talks to `web` | HTTP JSON at `/api/v1` |

`web/` never opens PostgreSQL. It calls this API.

Phase 1 is auth only: register, login, refresh, logout, `/auth/me`, and `/health`. Passwords are hashed with argon2. The access token is a JWT that lives for 15 minutes. The refresh token is random, stored as a SHA-256 hash, and set as an httpOnly cookie named `refresh_token` (`SameSite=Lax`, `Path=/`, 14 days). It is not in the JSON body.

Public registration always creates a `customer`. A date of birth under 21 in `Asia/Kolkata` is rejected and no row is written. On startup, if `ADMIN_EMAIL` is set and that email does not exist yet, the API creates an admin from `ADMIN_PASSWORD`, `ADMIN_NAME`, and `ADMIN_DATE_OF_BIRTH`. If that date is missing or under 21, the process exits and does not create the user. An email that already exists is left unchanged.

## Run locally

From the repo root, start PostgreSQL 16. The compose file publishes it on host port **5434** so it does not collide with a Postgres already listening on 5432:

```bash
docker compose up -d db
```

Then, in `api/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- OpenAPI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

The example admin in `.env.example` is local only (`admin@example.com` / `change-me-admin-password`). Change it before any shared machine.

`docker compose up` also builds this app. Day to day, running the API on the host is enough.

## Tests

PostgreSQL must be up. Pytest creates `ash_cedar_test` beside the app database and runs Alembic against it. It does not use SQLite.

```bash
source .venv/bin/activate
pytest
```

Override the test URL with `TEST_DATABASE_URL` if your Postgres user or port differs.
