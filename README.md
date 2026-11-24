# Ash & Cedar — Imported Cigar & Cigarette Store

Age-verified storefront for **imported cigars, imported cigarettes, lighters, and accessories** (cutters, ashtrays, and related tools), plus a separate admin console to add and remove products.

Working brand name: **Ash & Cedar**. Rename it in one place later (`web/src/lib/brand.ts`, created in Phase 1). The layout of the home page follows the structure of [theslowdraw.com](https://theslowdraw.com/), with original copy, original product data, and no use of that site’s name, founder, or company details.

## Apps (separate folders)

| Folder | Role | Stack |
|--------|------|--------|
| **`api/`** | Backend REST API | Python, FastAPI, PostgreSQL |
| **`web/`** | Storefront + admin console | TypeScript, Next.js, React, Tailwind |
| **`docs/`** | Design docs / contracts | Markdown |

`web` talks to `api` over HTTP only (`/api/v1`). They are independent projects with their own dependencies.

## Status
**Design / documentation phase.** `api/` and `web/` exist as separate folders. Application code inside them starts at Phase 1, after you confirm each phase before the next one begins.

## Database
**PostgreSQL 16**, used only by `api/`. `web/` has no database connection.

## What “finished” means
The launch path is Phases **1 → 6, then 8 → 9**: a separate `api/` and `web/`, PostgreSQL, the home page, admin catalog, cart, orders with shipping, account and email, demo data, tests on GitHub Actions, and a Docker Compose file you can deploy.

Phase 7 (sampler, gifts, partners) and Phase 10 (card or UPI payment) are optional. Payment is added only when a provider accepts this product category. Until then an order is saved as placed and the shop confirms payment. That is a real checkout, not a hidden gap.

## Documentation
Start here: **[docs/README.md](./docs/README.md)**

| Doc | Description |
|-----|-------------|
| [Project overview](./docs/01-project-overview.md) | What we sell, who uses it, compliance rules |
| [Architecture](./docs/02-architecture.md) | `api/` + `web/`, layers, and why this stack |
| [Database](./docs/03-database.md) | Tables, relationships, money and stock rules |
| [API & types](./docs/04-api-structure.md) | Routes the UI will call |
| [Flows](./docs/05-flows.md) | Register, browse, admin, cart, order |
| [Folder structure](./docs/06-folder-structure.md) | Planned files and frontend libraries |
| [Home page](./docs/08-homepage.md) | Section-by-section spec from the screenshots |
| [Features & phases](./docs/07-features-and-phases.md) | Backlog and MVP |
| [Implementation phases](./docs/phases/README.md) | Build order, E2E checklists, one prompt per phase |

## House rules
- Sell only to adults **21+**
- Show the statutory tobacco warning in the footer
- Customers cannot create admin accounts
- Do not claim a brand authorisation the business does not actually hold

## Disclaimer
Tobacco products are age-restricted. This project is a store plan for lawful adult retail. It is not medical, legal, or tax advice. Have a lawyer review policies, GST invoicing, and state-wise sale rules before launch.
