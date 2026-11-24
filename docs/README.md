# Documentation Index

Project: **Ash & Cedar — Imported Cigar & Cigarette Store**

This folder holds design documents only. Application code is not implemented yet.

| Document | Purpose |
|----------|---------|
| [01-project-overview.md](./01-project-overview.md) | What we are building, users, pages, and compliance |
| [02-architecture.md](./02-architecture.md) | System architecture, layers, stack, and why we chose it |
| [03-database.md](./03-database.md) | Relational schema, relationships, stock and price rules |
| [04-api-structure.md](./04-api-structure.md) | API routes and request/response shapes |
| [05-flows.md](./05-flows.md) | End-to-end customer and admin flows |
| [06-folder-structure.md](./06-folder-structure.md) | Separate `api/` + `web/` layout and libraries |
| [07-features-and-phases.md](./07-features-and-phases.md) | Feature list and high-level phases |
| [08-homepage.md](./08-homepage.md) | Home page sections taken from the reference screenshots |
| [phases/](./phases/README.md) | **Build order:** implementation phases, E2E gates, copy-paste prompts |

**Rule for implementation later:** database models → Pydantic/TS types → API contracts → services → repositories → UI. Types must stay in sync with the schema documented here.

**Rule for scope:** each file in `phases/` has its own prompt at the bottom. Implement that phase in the separate `api/` and `web/` folders, test the checklist, then wait for confirmation before the next phase. Database is PostgreSQL 16, used only by `api/`. Launch order is Phases 1–6, then 8, then 9. Phases 7 and 10 are optional. Do not invent tables or routes that contradict these docs.
