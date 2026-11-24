# 04 — API Structure

Base path: `/api/v1`

JSON fields: `snake_case`, matching the database.

Auth header on protected routes: `Authorization: Bearer <access_token>`

Refresh token: httpOnly cookie `refresh_token` (see `02-architecture.md`). The login JSON body also returns `access_token` and a public user. It does **not** return the raw refresh token to JavaScript.

## Common types

```text
Money is a string with two decimals in JSON ("5803.00") so JavaScript does not round it.
Timestamps are ISO-8601 with timezone.
UUIDs are strings.
```

### Error
FastAPI shape:

```json
{ "detail": "Email already registered" }
```

Validation errors use FastAPI’s 422 list. The web forms show the first message.

| Status | When |
|--------|------|
| 400 | Bad quantity, empty cart, under-age DOB |
| 401 | Missing or expired access token |
| 403 | Customer called an admin route, or cart while `age_verified` is false |
| 404 | Unknown id or unpublished product on a public route |
| 409 | Duplicate email, duplicate SKU, insufficient stock |
| 422 | Schema validation |

### Page
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 12
}
```

Default `page_size` is 12. Max 48.

### UserPublic
```json
{
  "id": "uuid",
  "email": "a@b.com",
  "full_name": "Asha Rao",
  "phone": "9876543210",
  "role": "customer",
  "age_verified": true
}
```

### ProductCard
Used on home carousels and category grids. Spec fields are null when the category does not use them.

```json
{
  "id": "uuid",
  "slug": "montecristo-no-2",
  "name": "Montecristo No. 2",
  "brand": "Montecristo",
  "category_slug": "cigars",
  "category_name": "Cigars",
  "subtype": "habano",
  "price_inr": "5803.00",
  "box_price_inr": "131875.00",
  "units_per_box": 25,
  "units_per_pack": null,
  "stock_qty": 1,
  "low_stock": true,
  "in_stock": true,
  "origin_country": "Cuba",
  "origin_label": "Vuelta Abajo",
  "smoking_time_min_minutes": 75,
  "smoking_time_max_minutes": 90,
  "intensity": 4,
  "strength": "medium_to_full",
  "shape": "figurado",
  "size_label": "6\" × 52",
  "is_founder_pick": true,
  "founder_rank": 1,
  "is_new_arrival": false,
  "primary_image": {
    "id": "uuid",
    "public_path": "/api/v1/media/products/....webp",
    "alt_text": "Montecristo No. 2"
  },
  "ratings": [
    { "source_name": "Cigar Aficionado", "score": "96.0" }
  ],
  "extra_ratings_count": 3
}
```

`low_stock` is true when `0 < stock_qty <= low_stock_threshold`.
`ratings` on the card is at most two. `extra_ratings_count` is the remainder.

### ProductDetail
`ProductCard` plus:

```json
{
  "description": "Longer text.",
  "short_description": "One line.",
  "sku": "CIG-001",
  "images": []
}
```

### ProductAdmin
`ProductDetail` plus `is_published`, `deleted_at`, `low_stock_threshold`, `founder_rank`, all nullable spec fields, and `category_id`.

### Cart
```json
{
  "id": "uuid",
  "items": [
    {
      "id": "uuid",
      "quantity": 1,
      "line_total_inr": "5803.00",
      "product": {}
    }
  ],
  "subtotal_inr": "5803.00"
}
```

`product` is a `ProductCard`. If the product was unpublished after it entered the cart, the item stays and `product.in_stock` is false with a flag `unavailable: true` so checkout can block.

---

## Health

### `GET /health`
Auth: no

```json
{ "status": "ok" }
```

---

## Auth

### `POST /auth/register`
Auth: no

Request:

```json
{
  "full_name": "Asha Rao",
  "email": "asha@example.com",
  "phone": "9876543210",
  "password": "at least 8 chars",
  "date_of_birth": "1990-04-12"
}
```

- `phone` may be omitted or null
- Ignores any `role` field if a client sends one
- 400 if age < 21 at today’s date in `Asia/Kolkata`
- 409 if email exists
- Creates `customer`, `age_verified=true`, starts a session (same response as login)

Response `201`: `TokenResponse`

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {}
}
```

Sets cookie `refresh_token`.

### `POST /auth/login`
```json
{ "email": "asha@example.com", "password": "..." }
```
401 on bad credentials. Same `TokenResponse` and cookie. Inactive users get 403.

### `POST /auth/refresh`
Auth: refresh cookie. Rotates the refresh token (old row `revoked_at` set). Returns a new access token and user.

### `POST /auth/logout`
Revokes the refresh token and clears the cookie. 204.

### `GET /auth/me`
Auth: access token. Returns `UserPublic`.

### `PATCH /auth/me`
Phase 8. Auth: access token.

```json
{ "full_name": "Asha Rao", "phone": "9876543210" }
```

Cannot change `email`, `role`, or `date_of_birth` here. Returns `UserPublic`.

### `POST /auth/change-password`
Phase 8. Auth: access token.

```json
{ "current_password": "...", "new_password": "at least 8 chars" }
```

204. Wrong current password is 400.

### `POST /auth/forgot-password`
Phase 8. Auth: no.

```json
{ "email": "asha@example.com" }
```

Always `202` with `{ "detail": "If an account exists for that email, a reset link is on its way." }` whether or not the email is registered. Sends mail only when the user exists and is active. Raw token is never returned in JSON.

### `POST /auth/reset-password`
Phase 8. Auth: no.

```json
{ "token": "raw token from the email", "new_password": "at least 8 chars" }
```

204 on success. 400 if the token is missing, expired, or already used.

---

## Public catalog

All of these are unauthenticated. They only return products with `is_published = true` and `deleted_at IS NULL`.

### `GET /categories`
```json
{
  "items": [
    { "id": "uuid", "slug": "cigars", "name": "Cigars", "description": null, "sort_order": 1 }
  ]
}
```

### `GET /categories/{slug}/products`
Query: `page`, `page_size`, `origin` (matches `origin_country`, case-insensitive), `q` (name or brand substring).

Response: page of `ProductCard`.

Unknown slug: 404.

### `GET /products/featured`
Cigars only. Published, non-deleted, `is_founder_pick = true`, ordered by `founder_rank` then name. Unpaged list, cap 12. Other categories are never included.

### `GET /products/new-arrivals`
`is_new_arrival = true`, newest first, cap 12.

### `GET /products`
Query: `q` (name or brand substring), `page`, `page_size`, `origin`, `new`.

- No `q` and no `new`: return an empty page (do not dump the whole catalog). `origin` by itself does not change that.
- `q`: match name or brand across categories. `origin` narrows `origin_country` when `q` or `new` is also set.
- `new=1`: only `is_new_arrival` products, newest first. May be combined with `q`.

Page of `ProductCard`. Header search uses `q`. The home page “view all new arrivals” link uses `new=1`.

### `GET /products/{slug}`
`ProductDetail`. 404 if missing or not public.

### `GET /brands`
Distinct `brand` values on public products, sorted A–Z.

```json
{ "items": ["Montecristo", "Oliva"] }
```

### `GET /media/products/{storage_filename}`
Streams the file. 404 if the file is missing, or the parent product is unpublished or soft-deleted. Unpublished and soft-deleted images are served only to an admin at `GET /admin/media/products/{storage_filename}`. Published images are public. `storage_key` is a random filename, not the original upload name.

---

## Cart
Auth: customer or admin, and `age_verified` must be true. Otherwise 403.

### `GET /cart`
Returns the active cart, creating an empty one if needed.

### `POST /cart/items`
```json
{ "product_id": "uuid", "quantity": 1 }
```
If the line exists, quantity **increases** by the amount (still capped by stock). 409 if the resulting quantity exceeds stock or the product is not public.

### `PATCH /cart/items/{item_id}`
```json
{ "quantity": 2 }
```
409 if over stock. Quantity must be ≥ 1. Use DELETE to remove.

### `DELETE /cart/items/{item_id}`
204.

---

## Orders
Auth: same as cart.

### `GET /checkout/summary`
Phase 6. Auth: same as cart. Reads the active cart and returns the numbers the checkout page shows. Does not create an order.

```json
{
  "subtotal_inr": "5803.00",
  "shipping_inr": "150.00",
  "total_inr": "5953.00",
  "free_shipping_over_inr": "10000.00"
}
```

### `POST /orders`
```json
{
  "customer_name": "Asha Rao",
  "customer_phone": "9876543210",
  "shipping_line1": "Flat 1",
  "shipping_line2": null,
  "city": "Mumbai",
  "state": "Maharashtra",
  "postal_code": "400001",
  "notes": "Call before delivery"
}
```

409 if cart is empty, any line is unavailable, or stock changed. On success, status is `placed`, cart becomes `converted`, a new active cart is empty.

Response `201`: `OrderDetail`.

### `GET /orders`
Page of the current user’s orders, newest first. Summary:

```json
{
  "id": "uuid",
  "order_number": "AC-00000012",
  "status": "placed",
  "subtotal_inr": "5803.00",
  "shipping_inr": "150.00",
  "total_inr": "5953.00",
  "created_at": "2026-11-23T08:00:00Z"
}
```

### `GET /orders/{id}`
`OrderDetail` with `order_items` and the shipping block. 404 if the order belongs to someone else (do not 403, so we do not reveal that the id exists).

---

## Contact

### `POST /contact`
Auth: no. Entry gate is UI-only; the API still accepts the post so a direct call works. Rate limits for contact, login, register, and forgot-password are Phase 9 (5 contact posts per IP per hour).

```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "phone": null,
  "subject": "Stock question",
  "message": "Do you ship to Guwahati?"
}
```

201:

```json
{ "id": "uuid", "status": "new" }
```

---

## Admin
Every route below: access token and `role = admin`. Otherwise 401 or 403.

### `GET /admin/products`
Query: `page`, `page_size`, `category`, `q`, `include_deleted` (default false), `status`.

When `status` is set, it defines the rows and `include_deleted` is ignored:

| status | Rows |
|--------|------|
| `published` | published, not deleted |
| `hidden` | not published, not deleted |
| `deleted` | `deleted_at` is set |
| `low_stock` | published, not deleted, `stock_qty <= low_stock_threshold` (this includes 0) |

When `status` is omitted, the list is non-deleted products, plus deleted rows only if `include_deleted=true`.

Response: page of `ProductAdmin`. `total` is the count for the whole filter, not the length of `items`. The dashboard reads `total` with `page_size=1` for published, hidden, and deleted, and uses `status=low_stock` for the short list. On the storefront, stock 0 is “Out of stock”; the “Only N left” pill is only when stock is above 0.

### `POST /admin/products`
JSON body with the writable product fields. `is_published` defaults false so a half-finished product does not hit the store. 409 on duplicate `sku` or `slug`.

Writable fields: `category_id` or `category_slug` (accept slug for easier forms), `sku`, `slug` (optional — server generates from name), `name`, `brand`, `subtype`, `short_description`, `description`, `price_inr`, `box_price_inr`, `units_per_box`, `units_per_pack`, `stock_qty`, `low_stock_threshold`, `origin_country`, `origin_region`, `origin_label`, smoking-time fields, `intensity`, `strength`, `shape`, `length_inches`, `ring_gauge`, `size_label`, `is_founder_pick`, `founder_rank`, `is_new_arrival`, `is_published`, `ratings` (array of `{source_name, score, sort_order}` replaces the set).

The service returns 400 unless `price_inr` > 0 and `stock_qty` >= 0. `is_founder_pick`, `founder_rank`, and a non-empty `ratings` array are allowed only when the category slug is `cigars`. `founder_rank` is an integer ≥ 1 when the flag is true, and null when the flag is false.

Response `201`: `ProductAdmin`.

### `GET /admin/products/{id}`
`ProductAdmin` including soft-deleted.

### `PATCH /admin/products/{id}`
Partial update. Same writable fields and the same 400 rules as create. Ratings array, if present, replaces all ratings for that product.

### `DELETE /admin/products/{id}`
Soft delete. 204. Idempotent if already deleted.

### `POST /admin/products/{id}/restore`
Clears `deleted_at`. Does not auto-publish. Returns `ProductAdmin`.

### `POST /admin/products/{id}/images`
`multipart/form-data`: `file`, optional `alt_text`, optional `is_primary`. JPEG, PNG, or WebP, max 5 MB, max 6 images on the product. 400 when the file fails those checks. 201 image object. First image becomes primary if none exists.

### `PATCH /admin/products/{id}/images/{image_id}`
`{ "alt_text": "...", "sort_order": 0, "is_primary": true }`

### `DELETE /admin/products/{id}/images/{image_id}`
Deletes the row and the file. 204. If the primary was deleted, the lowest `sort_order` remaining becomes primary.

### `GET /admin/orders`
Page of all orders. Query `status`.

### `GET /admin/orders/{id}`
Any customer’s order.

### `PATCH /admin/orders/{id}`
```json
{ "status": "confirmed" }
```
Allowed transitions:

```text
placed → confirmed → packed → shipped → delivered
placed → cancelled
confirmed → cancelled
```

Cancelling does **not** automatically restock in v1 (document the manual stock edit). Auto-restock can be added later; skipping it avoids double stock if the admin already adjusted the shelf.

### `GET /admin/messages`
Page of contact messages. Query `status`.

### `PATCH /admin/messages/{id}`
```json
{ "status": "read" }
```

---

## TypeScript mirror
`web/src/types/api.ts` copies these shapes. Phase 1 creates the auth types. Later phases add catalog, cart, and order types in the same file. Do not generate a second conflicting types package.
