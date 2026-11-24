# 07 — Features & Build Phases

## Feature backlog

### Platform
- [ ] Age gate (21+, session)
- [ ] Customer register / login / logout / refresh
- [ ] Bootstrap admin from environment
- [ ] `/auth/me` and account page
- [ ] Role redirect (register → `/account`, customer login → `/`, admin → `/admin`)

### Storefront
- [ ] Announcement bar with Login
- [ ] Navbar: Home, Cigars, Cigarettes, Lighters, Accessories, Contact Us
- [ ] Search, account, and cart icons
- [ ] Footer, statutory warning, house 21+ line
- [ ] Category listing pages
- [ ] Product detail
- [ ] Home page sections in `08-homepage.md` (core set)
- [ ] Contact form

### Catalog admin
- [ ] List products
- [ ] Add product (including specs, ratings, flags)
- [ ] Edit product
- [ ] Upload, reorder, and delete images
- [ ] Publish / unpublish
- [ ] Remove (soft delete) and restore

### Selling
- [ ] Cart for logged-in 21+ customers
- [ ] Checkout with subtotal, flat shipping, and total
- [ ] Order saved as `placed` (shop confirms payment; no card capture yet)
- [ ] Customer order history
- [ ] Admin order status
- [ ] Admin contact inbox
- [ ] Low-stock list on the admin dashboard

### Public-site bar (required before GitHub / deploy)
- [ ] Profile edit, change password, forgot password
- [ ] Order and reset emails (SMTP, or API log when SMTP is unset)
- [ ] One-command Docker Compose with PostgreSQL, migrations, and demo products
- [ ] README a reviewer can follow, plus demo logins
- [ ] GitHub Actions for API tests and a web typecheck
- [ ] 404 page, page titles, sitemap, draft legal pages
- [ ] Rate limits and basic security headers
- [ ] Deploy notes for a single Docker server

### Optional after launch
- [ ] Sampler builder (“pick five”)
- [ ] Gift-pack builder
- [ ] Partner / stockist logo band
- [ ] Card or UPI gateway, only with a provider that accepts this category
- [ ] Automatic restock on cancel
- [ ] S3 for images
- [ ] GST invoice PDF

---

## Phase plan

Detail, exit checklists, and copy-paste prompts:

→ **[docs/phases/README.md](./phases/README.md)**

| # | Phase | Covers the original request |
|---|--------|------------------------------|
| 0 | Design docs | This folder |
| 1 | Foundation, register, login, roles, age gate | Login and register |
| 2 | Catalog API, navbar, category pages, contact page shell | Navbar, database reads |
| 3 | Home page | Screenshots |
| 4 | Admin add / edit / remove products | Admin website |
| 5 | Cart | Needed to sell |
| 6 | Orders, shipping, contact inbox | Needed to sell |
| 7 | Extra merchandising | Optional. Sampler, gifts, partners |
| 8 | Account and email | Needed to publish |
| 9 | README, demo data, CI, Docker, deploy | Needed for GitHub and a real host |
| 10 | Card or UPI payment | Optional. Only with a real provider |

**Launch is Phases 1–6, then 8, then 9.** Phase 7 and Phase 10 are optional and do not block a portfolio push or a deploy.

**Rule:** implement and test one phase end-to-end before starting the next.

---

## What “done” means
A reviewer can clone the repo, run Docker Compose, and use a stocked shop: register, browse, cart, place an order, and manage products as admin. Reset-password and order mail work (real SMTP or the API log). The README and GitHub Actions are in place.

That is a site you can push to GitHub and deploy. It is not a card-payment shop, and it does not include the sampler or gift builder unless you later ask for Phase 7.

---

## Map from your points to documents

| Point | Where it is specified |
|-------|------------------------|
| 1. Login and register | `05-flows.md` §2–3, Phase 1 |
| 2. Navbar | `01-project-overview.md`, Phase 2 |
| 3. Home page from screenshots | `08-homepage.md`, Phase 3 |
| 4. Admin add and remove | `04-api-structure.md` admin section, Phase 4 |
| 5. Database | `03-database.md` |
| 6. File structure and why | `02-architecture.md`, `06-folder-structure.md` |
