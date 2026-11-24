# 01 — Project Overview

## Project name
**Ash & Cedar** (working brand)

Working repo folder: `imported-cigar-store`

The brand name is a placeholder. Implementation keeps it in `web/src/lib/brand.ts` so a rename does not require a schema change.

## Repo layout (important)
Two **separate** application folders plus docs:

| Folder | Meaning |
|--------|---------|
| `api/` | Backend — Python / FastAPI |
| `web/` | Frontend — TypeScript / Next.js / React (storefront **and** admin console) |
| `docs/` | Design documents (this folder) |

`web` never uses the database directly. It only calls `api` over HTTP.

The admin console is a **separate area of the same frontend** (`/admin`), not a third codebase. Customers never see that layout. Admins never use the store navbar while they are managing products. Reasons are in `02-architecture.md` and `06-folder-structure.md`.

## One-line summary
An age-verified online store for imported cigars, imported cigarettes, lighters, and accessories, with a role-gated admin console to add and remove products.

## What we sell

| Navbar item | Route | What belongs here |
|-------------|--------|-------------------|
| Home | `/` | Editorial landing page (see `08-homepage.md`) |
| Cigars | `/cigars` | Imported cigars |
| Cigarettes | `/cigarettes` | Imported cigarettes |
| Lighters | `/lighters` | Lighters and lighter inserts |
| Accessories | `/accessories` | Cigar cutters, ashtrays, and related tools |
| Contact Us | `/contact` | Enquiry form |

Icons in the header, not extra nav words: **search**, **account**, **cart**. A **Login** button sits in the top announcement bar.

Spelling used in the product: **Cigarettes**, **Lighters**. Category labels are plural because each page lists many products.

## Reference
Home page **layout** follows screenshots of [https://theslowdraw.com/](https://theslowdraw.com/) (November 2026): announcement bar, script logo, hero, trust cards, brand row, scored product carousel, founder note, origin cards, new arrivals, then richer merchandising blocks and a legal footer.

We copy the **section structure and visual tone** (warm paper background, gold accents, dark pill buttons, product spec cards). We do **not** copy that site’s trade name, founder story, company registration, addresses, phone numbers, or authorisation claims (Habanos specialist, Davidoff merchant, and similar). Product names in the screenshots are examples of card layout only. Our catalog is whatever an admin enters.

## Who uses it

| Actor | Can do |
|-------|--------|
| Visitor | Pass the 21+ gate, browse, search, open Contact Us |
| Customer | Register, login, add to cart, place an order |
| Admin | Everything a customer can do, plus add / edit / remove products and see orders and contact messages |

There is one login page. After login, a safe relative `next` path wins when it is present. Otherwise `role = admin` goes to `/admin` and `role = customer` goes to `/`. Register sends the new customer to `/account`.

## What we will build
1. **Auth** — register, login, JWT session, logout, customer vs admin
2. **Age gate** — 21+ interstitial before the store, plus date of birth checked on register
3. **Store chrome** — announcement bar, navbar, footer, statutory warning
4. **Home page** — sections in `08-homepage.md`
5. **Category and product pages** — four departments, product detail, quantity, Add
6. **Admin console** — create, edit, remove products, upload photos, publish or hide
7. **Cart and orders** — so a published product can actually be purchased
8. **Contact Us** — messages stored for admin to read

## What we are not building in the first versions
- A blog or cigar-journal CMS
- Live chat other than a WhatsApp link in the corner (static, optional)
- Multi-warehouse inventory
- Reviews written by customers
- Subscriptions / “cigar of the month” billing
- A payment-gateway integration in the early phases (see orders below)
- Scraping theslowdraw.com or any other catalog

## How an order is paid
Many card gateways refuse tobacco merchants. Phase 6 creates the order as **placed, awaiting confirmation**. The customer sees a clear status. Online card checkout (Razorpay or similar) is a later addition only if the business has a provider that accepts this category. Do not fake a successful payment.

Prices the admin enters are the **customer-facing price in INR** (what the buyer pays for one unit). The API does not compute GST, cess, or MRP ladders. Invoice formatting is a business/legal step before launch, not an early coding phase.

## Compliance the product must enforce
These are product rules, not a legal opinion:

- **House minimum age is 21.** Every web route (store, login, register, account, and `/admin`) stays behind the 21+ gate until that tab confirms. Register stores date of birth and rejects under 21, using the calendar date in `Asia/Kolkata`. Cart and order routes require `age_verified` on the server.
- **Statutory warning** is always visible in the footer: tobacco smoking is injurious to health, and the COTPA Act 2003 prohibits sale to persons under 18. Our house rule is stricter (21+).
- **No self-serve admin.** Registration always creates `customer`. The first admin comes from environment variables on the API.
- **No authorisation badges we cannot prove.** The “brands we carry” row lists brands that exist on published products. It must not say “authorised merchant” for a house we have not been authorised by.
- **No health claims.** Copy describes origin, format, and strength. It does not say a product is safe.
- **Photos** must be files the business owns or is licensed to use. Admins upload them. We do not hotlink the reference site.

State rules, advertising limits, and GST treatment change. A lawyer should review the live site before it takes money.

## Success criteria
The project is ready to push and deploy when Phases 1–6, 8, and 9 are confirmed:
- A new customer can register (21+), log in, reset a password, and log out
- Navbar reaches all four departments and Contact Us
- Home page shows the reference sections, with products from the database
- An admin can add a product, see it on the store, remove it, and see it disappear
- A customer can place an order with a shipping total; stock cannot be oversold
- `docker compose up` boots PostgreSQL, `api/`, and `web/` with demo products
- README and GitHub Actions let a reviewer run the project without a guided tour

Phase 7 and Phase 10 are optional. Card payment is not required for that bar.

## Primary tech direction
- **`api/`:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, JWT, local file storage for images
- **`web/`:** TypeScript, React, Next.js (App Router), Tailwind CSS, TanStack Query, React Hook Form + Zod
- **Types:** Pydantic schemas in `api/`, mirrored TypeScript types in `web/src/types`, both taken from `03-database.md` and `04-api-structure.md`

## Positioning statement
> Age-verified storefront and admin console for imported cigars, cigarettes, lighters, and accessories: FastAPI catalog and orders, PostgreSQL, and a Next.js shop whose home page follows a luxury retail layout.
