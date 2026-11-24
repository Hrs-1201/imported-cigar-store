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

Application code is not written yet. Implementation starts at Phase 1, and only after you paste that phase’s prompt.

Prompt and checklist: [`docs/phases/01-foundation-auth.md`](../docs/phases/01-foundation-auth.md)
