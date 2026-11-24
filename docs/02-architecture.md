# 02 — Architecture

## Goals of the architecture
- One storefront and one admin console, both real websites a person can click through
- Keep **`api/` and `web/` as separate projects** that communicate only via REST JSON
- Keep catalog rules (price, stock, age, role) on the server, not only in the browser
- Match the visual structure of the reference home page without coupling the UI to a CMS for every sentence

## Repo split

| Project folder | Responsibility |
|----------------|----------------|
| `api/` | FastAPI backend, PostgreSQL, auth, product images, orders |
| `web/` | Next.js UI — storefront routes and `/admin` routes; calls `api` only |
| `docs/` | Shared contracts (schema, API types, flows, homepage spec) |

## Why one `web/` app contains the admin console

The admin area is a second website in the browser (`/admin` has its own layout, nav, and pages). It is not a second repository.

| Approach | Decision |
|----------|----------|
| Routes under `web/src/app/admin` | **Use this** |
| A third app `admin/` with its own `package.json` | Do not, for this project |

Why:
- Customers and admins share login, types, and the API client
- Product cards and forms should look like the same brand
- One deploy, one `NEXT_PUBLIC_API_BASE_URL`
- Role checks still live on the API, so a customer who types `/admin` gets rejected even if the UI fails

A later split into two frontends is possible because the API is already separate. We do not need that split to meet “one admin website”.

## System context

```
Browser
    │
    ├── Storefront (/, /cigars, /cart, /contact, ...)
    └── Admin console (/admin/...)
            │
            ▼
web/  (Next.js + TypeScript + React)
    │  HTTPS / JSON  (/api/v1)
    ▼
api/  (FastAPI + Python)
    │
    ├── Auth (JWT, roles, 21+ date of birth)
    ├── Domain services (catalog, cart, orders, contact)
    ├── Repositories ──► PostgreSQL
    └── Image files ───► local disk (S3-compatible later)
```

## Logical layers (backend)

| Layer | Responsibility | Must not do |
|-------|----------------|-------------|
| **API (routers)** | Validate input, auth dependency, status codes, file upload limits | Pricing rules, raw SQL |
| **Schemas (Pydantic)** | Request/response contracts | DB sessions |
| **Services** | Age check, stock check, who may delete a product, order totals | HTTP details |
| **Repositories** | Queries and inserts | Business decisions such as “is this customer 21?” |
| **Models (ORM)** | Tables and relationships | Response JSON shape |

### Dependency rule
`Router → Service → Repository → Model/DB`

## High-level components

### 1. API service
- FastAPI app
- Versioned routes under `/api/v1`
- OpenAPI docs at `/docs` for development
- CORS limited to the Next.js origin

### 2. Auth
- Register / login / refresh / logout / me
- Access token (short-lived JWT) + refresh token (random, stored as a hash)
- Roles: `customer` | `admin`
- Public register can only create `customer`
- Bootstrap admin from environment variables if that email does not exist yet

### 3. Catalog
- Four fixed categories matching the navbar (seeded, not created by admin in the UI)
- Products belong to one category
- Public reads return only published, non-deleted, in-policy rows
- Admin reads return the full list, including hidden rows

### 4. Images
- Admin uploads JPEG, PNG, or WebP (max 5 MB each, max 6 images per product)
- Files live on disk under `api/storage/products/`
- API returns a URL the browser can load
- Phase 1–7 do not require S3. The storage path is behind one service so S3 can replace disk later without changing the product table’s public URL field

### 5. Cart and orders
- Cart is per logged-in customer (one active cart)
- Adding to cart requires auth and `age_verified = true`
- Placing an order copies price and product name onto the order line (catalog edits later must not rewrite history)
- Stock is decremented in the same transaction as the order
- Payment capture is **out of scope** until a provider is chosen. Status stays `placed`

### 6. Storefront UI
- Server and client components as Next.js App Router normally uses
- Data fetching for lists and mutations through TanStack Query
- Homepage marketing sections that do not change every day are React components (hero slides, trust cards, founder note, origin cards)
- Homepage product carousels read the API (founder picks, new arrivals)

Why marketing copy stays in code: the reference page is a designed layout, not a free-form CMS. Admins change **products**. They do not rearrange the hero in v1. That keeps Phase 4 to add/remove products, which is the requirement.

## Auth model (concrete)

| Token | Lifetime | Where it lives |
|-------|----------|----------------|
| Access JWT | 15 minutes | Memory only. A full page load or a new tab starts with no access token. |
| Refresh token | 14 days | httpOnly cookie `refresh_token`. JavaScript cannot read it. It is not in `localStorage` or `sessionStorage`. |

The browser calls same-origin `/api/v1/*`. Next.js rewrites that prefix to the API, so the cookie is first-party on port 3000. The API sets it `HttpOnly`, `SameSite=Lax`, `Path=/`. A new tab calls `/auth/refresh` with that cookie, stores the new access token in memory, and continues. The login JSON body does not include the refresh token. Phase 1 documents the rewrite in `web/README.md`.

## Age checks (two layers)

| Layer | Where | What it stops |
|-------|--------|----------------|
| Entry gate | `web` `sessionStorage` key `age_gate` = `21`, on every route including `/admin` | A tab that has not confirmed. Closing the tab clears it. It is not sent to the API. |
| Account | `api` on register and on cart/order | A forged UI. Server rejects DOB under 21 (`Asia/Kolkata`) and rejects cart and order routes when `age_verified` is false. |

The entry gate is a house UX rule. The server check is the one that matters for selling.

## Request path example (admin adds a product)

```
Admin form → POST /api/v1/admin/products  (Bearer access token)
  → router checks role == admin
  → service validates category slug, price > 0, stock >= 0
  → repository inserts product
  → response ProductAdmin
→ UI invalidates the public category query and the admin list
```

## Deployment shape (local first)

```
docker-compose.yml
  db      PostgreSQL 16
  api     uvicorn :8000
  web     next start :3000
```

Developers may also run PostgreSQL 16 in Docker and run `api` and `web` on the host. Both are acceptable in Phase 1. Minimum: the database is PostgreSQL 16, not an in-memory substitute.

## Why this stack

| Choice | Why we use it |
|--------|----------------|
| **PostgreSQL 16** | Users, products, carts, and orders are relational. Stock and order lines need transactions. Only `api/` connects to it. |
| **FastAPI** | Small Python API, automatic OpenAPI, Pydantic validation, same style as the other project in this folder. |
| **SQLAlchemy + Alembic** | Models match `03-database.md`. Schema changes are migration files, not hand-edited production databases. |
| **JWT access + refresh** | Login survives a short access-token life. Logout revokes the refresh token. |
| **Repository pattern** | Routers stay thin. Services can be tested without HTTP. |
| **Next.js App Router** | File-based routes map cleanly onto the navbar and `/admin`. |
| **TypeScript** | API shapes in `04-api-structure.md` become `web/src/types`. |
| **Tailwind CSS** | The reference layout is spacing, borders, and type — utilities are enough. No component-library theme to fight. |
| **TanStack Query** | Category pages, cart, and admin lists need cache, refetch, and loading state. |
| **React Hook Form + Zod** | Register, contact, and the long product form share one validation style. |
| **Local image disk** | No cloud account is required to finish admin uploads. |
| **No Redux** | There is no complex client state beyond the cart query and the age-gate flag. |

## Explicitly not in the architecture
- GraphQL
- Microservices per category
- Direct Postgres access from Next.js
- Scraping or embedding another shop’s catalog
- Client-side-only admin checks

## Environments

| Name | Used by | Examples |
|------|---------|----------|
| `DATABASE_URL` | api | `postgresql+psycopg://...` |
| `JWT_SECRET` | api | long random string |
| `CORS_ORIGINS` | api | `http://localhost:3000` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_NAME` / `ADMIN_DATE_OF_BIRTH` | api | bootstrap admin. DOB is required when the email is set, and it must be 21+. Example values in `.env.example` are local only. |
| `SHIPPING_FLAT_INR` / `FREE_SHIPPING_OVER_INR` | api | Phase 6. Copied onto each order. |
| `WEB_PUBLIC_URL` | api | Phase 8. Password-reset links. |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `MAIL_FROM` | api | Phase 8. Empty `SMTP_HOST` means the API logs the message. |
| `MEDIA_ROOT` | api | `./storage` |
| `NEXT_PUBLIC_API_BASE_URL` | web | `/api/v1` when using the rewrite, or `http://localhost:8000/api/v1` |

Secrets never go into `docs/` with real values. `.env.example` lists keys only, and it is created in Phase 1, not in this documentation pass.
