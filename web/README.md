# web

Storefront and admin UI for Ash & Cedar. This folder is a **separate project** from `api/`.

| | |
|--|--|
| Language | TypeScript |
| Framework | Next.js (App Router), React, Tailwind |
| Data | HTTP calls to `api` at `/api/v1` only |
| Database | **None.** PostgreSQL lives in `api/` |

Admin pages live under `/admin` in this same frontend. Phase 1 is the age gate, register, login, account, and an empty admin shell.

## Proxy

The browser talks only to this app on port 3000. `next.config.ts` rewrites `/api/v1/:path*` to `API_ORIGIN` (default `http://127.0.0.1:8000`).

Use `NEXT_PUBLIC_API_BASE_URL=/api/v1`, not the API’s port. Login and register then receive a first-party `refresh_token` cookie (`HttpOnly`, `SameSite=Lax`, `Path=/`). JavaScript cannot read it. The access token stays in memory. A full page load or a new tab calls `POST /auth/refresh` with that cookie before it has an access token. If a later call returns 401, the client refreshes once and retries. A failed refresh clears the memory token and sends the browser to `/login`.

Calling `http://127.0.0.1:8000` directly is only a fallback. The API allows CORS from `http://localhost:3000`, but the cookie will not be on port 3000 unless the rewrite is used.

## Run locally

Start PostgreSQL and the API first (`api/README.md`). Then, in `web/`:

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000. Every route, including `/login`, `/register`, `/account`, and `/admin`, stays behind the 21+ gate until this tab sets `sessionStorage.age_gate` to `21`. Leave sends the browser to https://www.google.com and does not set the flag.

- Register lands on `/account`.
- Login honors a safe relative `next` (`/login?next=/account`). Otherwise a customer goes to `/` and an admin goes to `/admin`.
- `/` is a short welcome. The full home page is a later phase. The store navbar, announcement bar, and footer wrap the public pages. Category, product, search, and contact pages read the API. The cart page says it arrives later. Login still lives in the announcement bar.
- `/admin` calls `GET /auth/me`. A customer gets 200 with `role=customer` and then sees a refusal, with no admin navigation. An admin sees an empty shell and can log out.

`docker compose up` can build this app as well. The image bakes `API_ORIGIN=http://api:8000` so the rewrite stays inside the compose network. The browser still uses `/api/v1` on port 3000.
