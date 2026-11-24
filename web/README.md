# web

Storefront and admin UI for Ash & Cedar. This folder is a **separate project** from `api/`.

| | |
|--|--|
| Language | TypeScript |
| Framework | Next.js (App Router), React, Tailwind |
| Data | HTTP calls to `api` at `/api/v1` only |
| Database | **None.** PostgreSQL lives in `api/` |

Admin pages live under `/admin` in this same frontend. They are a separate layout, not a third project, and they still go through the API.

Application code is not written yet. Implementation starts at Phase 1, and only after you paste that phase’s prompt.

Prompt and checklist: [`docs/phases/01-foundation-auth.md`](../docs/phases/01-foundation-auth.md)
