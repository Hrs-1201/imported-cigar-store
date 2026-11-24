# 03 — Database Document

## Goals
- Fully **relational** schema for an age-verified shop
- Support the four navbar departments, admin product CRUD, cart, orders, and contact messages
- Keep money as exact decimal rupees, not binary floats
- Keep order history stable after a product is edited or removed

## Database
- PostgreSQL 16
- UUID primary keys
- `TIMESTAMPTZ` for all timestamps
- `NUMERIC(12,2)` for money (INR). Never `FLOAT` / `DOUBLE`
- Soft conventions: `created_at`, `updated_at` on business tables

Images are files on disk. The database stores the storage key and the public URL path, not the file bytes.

## ER overview

```
users
  ├── refresh_tokens
  ├── password_reset_tokens
  ├── carts ── cart_items ──► products
  ├── orders ── order_items
  └── (admin actions are the same users row with role = admin)

categories
  └── products
        ├── product_images
        ├── product_ratings
        ├── cart_items
        └── order_items   (snapshot columns, FK kept for reference)

contact_messages   (standalone)
```

## Enums

```text
UserRole:        customer | admin
Strength:        mild | mild_to_medium | medium | medium_to_full | full
ProductShape:    parejo | toro | robusto | churchill | figurado | lancero | corona | gordo | other
CartStatus:      active | converted
OrderStatus:     placed | confirmed | packed | shipped | delivered | cancelled
ContactStatus:   new | read | archived
```

`ProductShape` applies to cigars. Other categories leave `shape` null.

Suggested `subtype` values (stored as text, not an enum, so admin can be specific):

| Category | Examples |
|----------|----------|
| cigars | habano, new_world |
| cigarettes | pack, carton |
| lighters | soft_flame, torch, butane_insert |
| accessories | cutter, ashtray, humidor, case |

## Fixed categories (seeded)

These four rows are inserted by a migration. Admin does not add a fifth department in v1, because the navbar is a fixed information architecture.

| slug | name | sort_order |
|------|------|------------|
| `cigars` | Cigars | 1 |
| `cigarettes` | Cigarettes | 2 |
| `lighters` | Lighters | 3 |
| `accessories` | Accessories | 4 |

---

## Tables

### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(320) | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |
| full_name | VARCHAR(200) | NOT NULL |
| phone | VARCHAR(20) | NULL |
| role | ENUM UserRole | NOT NULL DEFAULT `customer` |
| date_of_birth | DATE | NOT NULL |
| age_verified | BOOLEAN | NOT NULL |
| is_active | BOOLEAN | NOT NULL DEFAULT TRUE |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

`age_verified` is true only when `date_of_birth` is at least 21 years before the register timestamp. The API sets both. Clients cannot send `role` or `age_verified`.

Index: unique `(email)`

### `refresh_tokens`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users ON DELETE CASCADE |
| token_hash | TEXT | UNIQUE NOT NULL |
| expires_at | TIMESTAMPTZ | NOT NULL |
| revoked_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

Index: `(user_id)`, `(expires_at)`

### `password_reset_tokens`
Added in Phase 8. Not created in Phase 1.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users ON DELETE CASCADE |
| token_hash | TEXT | UNIQUE NOT NULL |
| expires_at | TIMESTAMPTZ | NOT NULL |
| used_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

The email link carries the raw token once. The database stores only the hash. Token lifetime: 30 minutes. Requesting a new link revokes older unused tokens for that user.

### `categories`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| slug | VARCHAR(40) | UNIQUE NOT NULL |
| name | VARCHAR(80) | NOT NULL |
| description | TEXT | NULL |
| sort_order | INT | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### `products`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| category_id | UUID | FK → categories |
| sku | VARCHAR(64) | UNIQUE NOT NULL |
| slug | VARCHAR(160) | UNIQUE NOT NULL |
| name | VARCHAR(200) | NOT NULL |
| brand | VARCHAR(120) | NOT NULL |
| subtype | VARCHAR(64) | NULL |
| short_description | VARCHAR(300) | NULL |
| description | TEXT | NULL |
| price_inr | NUMERIC(12,2) | NOT NULL CHECK (price_inr > 0) |
| box_price_inr | NUMERIC(12,2) | NULL |
| units_per_box | INT | NULL |
| units_per_pack | INT | NULL |
| stock_qty | INT | NOT NULL DEFAULT 0 CHECK (stock_qty >= 0) |
| low_stock_threshold | INT | NOT NULL DEFAULT 2 |
| origin_country | VARCHAR(80) | NULL |
| origin_region | VARCHAR(120) | NULL |
| origin_label | VARCHAR(160) | NULL |
| smoking_time_min_minutes | INT | NULL |
| smoking_time_max_minutes | INT | NULL |
| intensity | SMALLINT | NULL CHECK (intensity BETWEEN 1 AND 5) |
| strength | ENUM Strength | NULL |
| shape | ENUM ProductShape | NULL |
| length_inches | NUMERIC(4,2) | NULL |
| ring_gauge | SMALLINT | NULL |
| size_label | VARCHAR(80) | NULL |
| is_founder_pick | BOOLEAN | NOT NULL DEFAULT FALSE |
| founder_rank | INT | NULL |
| is_new_arrival | BOOLEAN | NOT NULL DEFAULT FALSE |
| is_published | BOOLEAN | NOT NULL DEFAULT FALSE |
| deleted_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

Indexes:
- `(category_id)` where `deleted_at IS NULL AND is_published`
- `(is_founder_pick, founder_rank)`
- `(is_new_arrival, created_at DESC)`
- `(brand)`

Slug is generated from `name` and made unique (`montecristo-no-2`, then `montecristo-no-2-2` if needed). Admin may edit the slug if it is still unique.

`is_founder_pick` and `product_ratings` are for cigars only. When the flag is true, `founder_rank` is required and is an integer ≥ 1. When the flag is false, `founder_rank` is null. The API returns 400 if another category sets the flag, the rank, or any rating row. `GET /products/featured` returns only published, non-deleted cigars with the flag set.

**Which columns the storefront shows**

| Column | Cigars | Cigarettes | Lighters | Accessories |
|--------|--------|------------|----------|-------------|
| brand, name, price, stock | yes | yes | yes | yes |
| smoking time, intensity, strength, shape, size, box | yes | strength and pack size only | no | no |
| origin_label | yes | yes | yes | optional |
| founder rank, ratings | yes | no | no | no |
| subtype | line under the category label | pack or carton | torch / insert | cutter / ashtray |

`size_label` is the display string when inches and ring gauge are not both set (example: `6" × 52`, or `King size`). If `length_inches` and `ring_gauge` are set, the API can also return a formatted size. Admin may type `size_label` directly; if empty, the API formats from length and ring gauge.

`origin_label` is the card line (example: `Made in USA`, `Vuelta Abajo`). `origin_country` powers the origin-card filters (`/cigars?origin=Cuba`).

### `product_images`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| product_id | UUID | FK → products ON DELETE CASCADE |
| storage_key | TEXT | NOT NULL |
| public_path | TEXT | NOT NULL |
| alt_text | VARCHAR(200) | NOT NULL |
| sort_order | INT | NOT NULL DEFAULT 0 |
| is_primary | BOOLEAN | NOT NULL DEFAULT FALSE |
| created_at | TIMESTAMPTZ | NOT NULL |

One primary image per product (partial unique index on `product_id` where `is_primary`). The card uses the primary image. Detail page uses all images in `sort_order`.

### `product_ratings`
Optional scores printed on cigar cards (the round badges in the screenshots).

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| product_id | UUID | FK → products ON DELETE CASCADE |
| source_name | VARCHAR(80) | NOT NULL |
| score | NUMERIC(4,1) | NOT NULL |
| sort_order | INT | NOT NULL DEFAULT 0 |
| created_at | TIMESTAMPTZ | NOT NULL |

The card shows the first two by `sort_order`. If more exist, the UI shows `+N more ratings`. Empty list means no badges. Do not invent scores.

### `carts`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users ON DELETE CASCADE |
| status | ENUM CartStatus | NOT NULL DEFAULT `active` |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

Partial unique: one `active` cart per `user_id`.

### `cart_items`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| cart_id | UUID | FK → carts ON DELETE CASCADE |
| product_id | UUID | FK → products |
| quantity | INT | NOT NULL CHECK (quantity > 0) |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

Unique: `(cart_id, product_id)`

Quantity cannot exceed `products.stock_qty` at add and at order time. If stock drops after the item is in the cart, checkout returns a conflict and asks the customer to lower quantity.

### `orders`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| order_number | VARCHAR(20) | UNIQUE NOT NULL |
| status | ENUM OrderStatus | NOT NULL DEFAULT `placed` |
| subtotal_inr | NUMERIC(12,2) | NOT NULL |
| shipping_inr | NUMERIC(12,2) | NOT NULL |
| total_inr | NUMERIC(12,2) | NOT NULL |
| customer_name | VARCHAR(200) | NOT NULL |
| customer_phone | VARCHAR(20) | NOT NULL |
| shipping_line1 | VARCHAR(200) | NOT NULL |
| shipping_line2 | VARCHAR(200) | NULL |
| city | VARCHAR(80) | NOT NULL |
| state | VARCHAR(80) | NOT NULL |
| postal_code | VARCHAR(12) | NOT NULL |
| notes | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

`order_number` format: `AC-` + 8 digits (example `AC-00001234`), from a Postgres sequence. Prefix matches the working brand initials; change the prefix if the brand is renamed before launch.

`total_inr = subtotal_inr + shipping_inr`. Shipping is a flat amount from API env (`SHIPPING_FLAT_INR`), or `0.00` when the subtotal is at least `FREE_SHIPPING_OVER_INR`. Both numbers are copied onto the order so a later env change does not rewrite history.

There is no `payment_status` column on the launch path. `placed` means the shop confirms payment offline (bank transfer, UPI, or cash on delivery — whichever the business actually offers). Phase 10 adds provider columns only after a real payment account exists. Do not mark an order paid inside the app until that provider confirms it.

### `order_items`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| order_id | UUID | FK → orders ON DELETE CASCADE |
| product_id | UUID | FK → products ON DELETE RESTRICT |
| product_name | VARCHAR(200) | NOT NULL |
| sku | VARCHAR(64) | NOT NULL |
| unit_price_inr | NUMERIC(12,2) | NOT NULL |
| quantity | INT | NOT NULL CHECK (quantity > 0) |
| line_total_inr | NUMERIC(12,2) | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

`ON DELETE RESTRICT` stops a hard delete of a product that was ordered. Admin “remove” is a soft delete (`deleted_at`), so the restriction is a backstop.

`line_total_inr = unit_price_inr * quantity`, computed in the service, stored so reports do not depend on live catalog prices.

### `contact_messages`
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(200) | NOT NULL |
| email | VARCHAR(320) | NOT NULL |
| phone | VARCHAR(20) | NULL |
| subject | VARCHAR(200) | NOT NULL |
| message | TEXT | NOT NULL |
| status | ENUM ContactStatus | NOT NULL DEFAULT `new` |
| created_at | TIMESTAMPTZ | NOT NULL |

Public insert. Only admins can list or change status.

---

## Stock and remove rules

| Action | Effect |
|--------|--------|
| Public catalog | `deleted_at IS NULL AND is_published = true` |
| Admin remove | Set `deleted_at = now()`, `is_published = false`. Row stays. |
| Admin restore | Clear `deleted_at`. Stays unpublished until admin publishes again. |
| Stock 0 | Product can stay published. Card shows out of stock and disables Add. |
| `stock_qty <= low_stock_threshold` and `stock_qty > 0` | Storefront badge `Only {stock_qty} left` |
| Admin low-stock list | Published, not deleted, `stock_qty <= low_stock_threshold`, including 0 |
| Place order | In one transaction: lock product rows, check quantity, insert order, decrement `stock_qty`, mark cart `converted` |

Remove is soft delete because order lines point at `product_id`, and a mis-click must be reversible. `sku` and `slug` stay unique after soft delete, so a removed product is restored rather than recreated under the same SKU. A duplicate SKU or slug returns 409.

## Public vs admin field sets

**Public `ProductCard`** omits `sku` and `deleted_at`. **`ProductDetail`** adds `sku`. **`ProductAdmin`** adds `sku`, `is_published`, and `deleted_at`. Never return `password_hash` or refresh token hashes.

**Customer user (public)** returns: `id`, `email`, `full_name`, `phone`, `role`, `age_verified`. Never `password_hash`, `date_of_birth` on the public profile response after register (DOB was only for the age check). Admin user dumps are out of scope; admins do not get a customer browser.

## Seed data
Phase 2 migration seeds the four categories only. Demo products are optional fixtures in `api/tests` or a `make seed-demo` script, clearly fake, so the home page can be screenshotted before the admin has typed a catalog. Demo seed is not required for Phase 2’s exit if empty states are correct. Phase 3’s exit is easier with at least four demo cigars and one item in each other category. The seed script must be idempotent and must not run automatically in production.

## What is not a table
| Thing | Where it lives | Why |
|-------|----------------|-----|
| Hero slides, trust cards, founder note, origin blurbs | React components | Designed layout, changes with a deploy |
| Statutory warning text | Footer component | Legal line, always on |
| Brand logo strip | Derived from distinct `products.brand` on published rows | Avoids a CMS and avoids false authorisation logos |
| Age-gate acknowledgement | Browser session | The real age check is `users.date_of_birth` |
