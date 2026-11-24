# 06 — Folder Structure

The repo is a **monorepo with two separate apps**:

| Folder | Role | Stack |
|--------|------|--------|
| **`api/`** | Backend / REST API | Python, FastAPI |
| **`web/`** | Storefront and admin UI | TypeScript, Next.js, React |

They are **independent projects** (own dependencies, Dockerfile, scripts). They talk only over HTTP JSON (`web` → `api` at `/api/v1`).

`docs/` is the design set. `api/` and `web/` already exist as separate folders, each with a README and no application code. The tree below is what later phases fill in. This documentation pass does not add that code.

```text
imported-cigar-store/
├── README.md
├── .env.example                      # compose only; no secrets
├── .gitignore
├── docker-compose.yml                # db + api + web
├── docs/
│   ├── README.md
│   ├── 01-project-overview.md
│   ├── 02-architecture.md
│   ├── 03-database.md
│   ├── 04-api-structure.md
│   ├── 05-flows.md
│   ├── 06-folder-structure.md
│   ├── 07-features-and-phases.md
│   ├── 08-homepage.md
│   └── phases/
│
├── api/
│   ├── README.md
│   ├── .env.example
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/versions/
│   ├── Dockerfile
│   ├── storage/products/             # gitignored uploaded images
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_catalog.py
│   │   ├── test_admin_products.py
│   │   ├── test_cart.py
│   │   └── test_orders.py
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py             # settings from env
│       │   ├── security.py           # password hash, JWT
│       │   ├── db.py                 # engine, session
│       │   └── deps.py               # current user, require admin
│       ├── models/
│       │   ├── user.py
│       │   ├── catalog.py            # categories, products, images, ratings
│       │   ├── cart.py
│       │   ├── order.py
│       │   └── contact.py
│       ├── schemas/
│       │   ├── auth.py
│       │   ├── catalog.py
│       │   ├── cart.py
│       │   ├── orders.py
│       │   └── contact.py
│       ├── repositories/
│       │   ├── user_repo.py
│       │   ├── catalog_repo.py
│       │   ├── cart_repo.py
│       │   ├── order_repo.py
│       │   └── contact_repo.py
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── catalog_service.py
│       │   ├── cart_service.py
│       │   ├── order_service.py
│       │   └── contact_service.py
│       └── api/v1/
│           ├── router.py
│           ├── health.py
│           ├── auth.py
│           ├── catalog.py
│           ├── media.py
│           ├── cart.py
│           ├── orders.py
│           ├── contact.py
│           └── admin.py
│
└── web/
    ├── README.md
    ├── .env.example
    ├── package.json
    ├── tsconfig.json
    ├── next.config.ts                # rewrite /api/v1 to the API origin
    ├── Dockerfile
    ├── public/
    └── src/
        ├── app/
        │   ├── layout.tsx            # age gate + store chrome
        │   ├── page.tsx              # home
        │   ├── login/page.tsx
        │   ├── register/page.tsx
        │   ├── cigars/page.tsx
        │   ├── cigarettes/page.tsx
        │   ├── lighters/page.tsx
        │   ├── accessories/page.tsx
        │   ├── search/page.tsx
        │   ├── products/[slug]/page.tsx
        │   ├── contact/page.tsx
        │   ├── cart/page.tsx
        │   ├── checkout/page.tsx
        │   ├── account/page.tsx
        │   ├── account/orders/page.tsx
        │   ├── legal/                 # short static policy stubs
        │   └── admin/
        │       ├── layout.tsx        # admin chrome, no store navbar
        │       ├── page.tsx
        │       ├── products/page.tsx
        │       ├── products/new/page.tsx
        │       ├── products/[id]/page.tsx
        │       ├── orders/page.tsx
        │       ├── orders/[id]/page.tsx
        │       └── messages/page.tsx
        ├── components/
        │   ├── age-gate/
        │   ├── layout/               # announcement, navbar, footer, warning
        │   ├── home/                 # one file per homepage section
        │   ├── catalog/              # ProductCard, spec grid, quantity
        │   ├── cart/
        │   ├── admin/
        │   └── ui/
        ├── lib/
        │   ├── api-client.ts
        │   ├── auth.ts
        │   └── brand.ts              # store name, tagline — rename here
        ├── hooks/
        └── types/
            └── api.ts
```

---

## Separation rules

1. No shared runtime package between Python and Next.js. Contracts live in `docs/04-api-structure.md`.
2. `api/` owns the database, password hashes, JWT secret, and image files.
3. `web/` owns routing and presentation. It never opens Postgres.
4. Each app has its own `README.md`, `.env.example`, and `Dockerfile`.
5. Root `docker-compose.yml` starts `db`, `api`, and `web`.
6. Local URLs:
   - API: `http://localhost:8000`
   - Web: `http://localhost:3000`
   - Browser calls `/api/v1/...` on port 3000; Next.js rewrites to port 8000

---

## Why each part of the tree exists

| Path | Why |
|------|-----|
| `api/app/api/v1/` | HTTP only. Easy to see the surface area. |
| `api/app/services/` | Age, stock, and order totals have one implementation. |
| `api/app/repositories/` | SQL stays out of the routers. |
| `api/app/models/` | Matches `03-database.md`. |
| `api/app/schemas/` | Matches `04-api-structure.md`. |
| `api/alembic/` | Schema is versioned. |
| `api/storage/products/` | Uploads are not rows of bytes in PostgreSQL. |
| `web/src/app/admin/` | Admin is a separate layout, same app. |
| `web/src/components/home/` | Homepage sections can be built one at a time against `08-homepage.md`. |
| `web/src/lib/brand.ts` | Brand rename does not touch the database. |
| `web/src/types/api.ts` | One TypeScript mirror of the API. |

## `web/` libraries

| Area | Library | Why |
|------|---------|-----|
| Language | TypeScript | Catch mismatched product fields before runtime |
| UI | React 19 | Component model fits cards, forms, and the admin table |
| Framework | Next.js App Router | Routes match the navbar and `/admin` |
| Styling | Tailwind CSS | Reference layout is utility-level: borders, radius, type scale |
| Server cache | TanStack Query | Refetch catalog after admin edits; cart count in the header |
| Forms | React Hook Form + Zod | Register, contact, checkout, and the product form |
| HTTP | `fetch` in `lib/api-client.ts` | Attach bearer token, one refresh retry on 401 |
| Icons | lucide-react | Search, account, cart, plus/minus |
| Toasts | sonner | “Added”, “Removed”, save errors |
| Dates | date-fns | Age calculation display; order dates |
| Lint / format | ESLint + Prettier | Consistent style |

### Fonts (from the reference tone, not their files)
| Role | Font | Why |
|------|------|-----|
| Logo script | `Great Vibes` (Google) | Script wordmark like the reference header |
| Headlines | `Fraunces` | High-contrast serif for hero and section titles |
| UI and body | `Outfit` | Readable nav, prices, and spec labels |

Load these with `next/font/google`.

### Visual tokens
Define in Tailwind theme, not scattered hex values:

| Token | Approx | Use |
|-------|--------|-----|
| `paper` | `#f7f4ee` | Page background |
| `ink` | `#1c1a17` | Headlines and dark buttons |
| `gold` | `#8c7340` | Script logo, eyebrows, thin card borders |
| `muted` | `#5c564c` | Secondary text |
| `warning` | `#c62828` | Statutory warning box only |

Buttons that mean “do the thing” (Add, Login, primary CTA) are **ink** pills with white text. Gold is for type and hairline borders, not for every button. That matches the screenshots.

### Not required
- Redux or Zustand
- A second admin framework (no Django admin, no Refine)
- shadcn as a requirement (allowed later if a primitive is taking too long)
- A payment SDK in Phases 1–6

## `api/` libraries

| Library | Why |
|---------|-----|
| FastAPI | Routes, dependency injection, OpenAPI |
| SQLAlchemy 2 | Models and queries |
| Alembic | Migrations |
| Pydantic v2 | Request and response models |
| PyJWT | Access tokens |
| pwdlib or passlib with bcrypt (or argon2-cffi) | Password hashes |
| psycopg | Postgres driver |
| pytest + httpx | API tests |
| python-multipart | Image upload |
| Pillow | Reject non-images and downscale the long edge to 1600px so cards stay light |

## Naming conventions
- Python modules: `snake_case`
- React components: `PascalCase` filenames
- API JSON: `snake_case`
- DB tables: plural `snake_case`
- Routes in the UI: plural department names (`/cigars`, `/cigarettes`, `/lighters`, `/accessories`)

## What exists today
`docs/`, the root `README.md`, and two empty app folders:

- `api/README.md` — backend project shell. Code starts in Phase 1.
- `web/README.md` — frontend project shell. Code starts in Phase 1.

They are already separate. Phase 1 fills them in. It does not merge them.
