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

## Catalog

Public routes need no token. They return products only when `is_published` is true and `deleted_at` is null. Money is a string with two decimals.

- `GET /categories`
- `GET /categories/{slug}/products` — `q`, `origin`, `page`, `page_size`
- `GET /products` — `q`, `origin`, `new=1`, `page`, `page_size`. The page is empty unless `q` or `new=1` is set. `origin` alone does not list the catalog.
- `GET /products/featured` — published founder-pick cigars, `{ "items": [] }`, cap 12
- `GET /products/new-arrivals` — same shape, newest first, cap 12
- `GET /products/{slug}`
- `GET /brands`
- `GET /media/products/{filename}` — 404 until that published image file is on disk
- `POST /contact` — saves a message. The admin inbox is later.

## Demo catalog (dev only)

`python -m app.scripts.seed_demo` loads the country brand lists: cigars from Cuba, the Dominican Republic, Nicaragua, and Honduras, and cigarettes from Russia, China, Japan, Ukraine, the United Kingdom, and Thailand. It also keeps one lighter, one cutter, one ashtray, and one unpublished cigar that the shop must not show. Prices and sizes are demo figures.

Photos attach only when a file is already in `api/storage/products/`. The current files are the Macanudo Vintage Maduro cigar and the two Sobranie pack views.

The command is idempotent. It removes the earlier fictional tobacco SKUs (`DEMO-CIG-001` through `DEMO-CIG-004`, `DEMO-CGT-001`, `DEMO-CGT-002`) if they are still present. It does not run on API startup. It refuses a database whose name ends in `_test`. Do not run it against production.
