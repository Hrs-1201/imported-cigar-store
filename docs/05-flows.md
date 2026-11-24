# 05 — Flows

Ages and roles are enforced on the API. The UI mirrors them so people do not fill a form that will be rejected.

## 1. Age gate

The gate wraps every web route: store, login, register, account, cart, and `/admin`. The flag is `sessionStorage` key `age_gate` with value `21`. It is not a cookie, not an account, and not sent to the API. Closing the tab clears it. A new tab asks again.

```
Visitor opens any route
  → no sessionStorage flag age_gate
  → full-screen panel:
       Ash & Cedar
       This shop sells tobacco products.
       You must be 21 or older to enter.
       [I am 21 or older]  [Leave]
  → 21+ sets the flag and shows the page
  → Leave sends the browser to https://www.google.com
```

The catalog HTTP API stays readable without this flag. Cart and order routes do not. Selling depends on date of birth at register and on `age_verified` on the server.

## 2. Register

```
/register
  fields: full name, email, phone (optional), password, confirm password, date of birth
  checkbox: I confirm I am 21 or older and I am not buying for a minor
  → POST /auth/register
  → API computes age in Asia/Kolkata
       under 21 → 400, form shows the message, no user row
       email taken → 409
       ok → user role=customer, cookie set, access token stored
  → redirect to /account
```

Password rules: minimum 8 characters. No maximum below 72. Hash with bcrypt or argon2 (pick one in Phase 1 and use it everywhere).

Confirm password and the 21+ checkbox are form checks only. They are not API fields. The form does not submit until both pass. The API still requires `date_of_birth` and rejects under 21.

## 3. Login

```
Announcement bar “Login” or /login
  email + password
  → POST /auth/login
  → 401 shows “Email or password is incorrect” (same message either way)
  → if `next` is a relative path (starts with `/`, not `//`), go there
  → else role admin → /admin
  → else role customer → /
```

There is no public “make me admin” control.

Bootstrap: on API startup, if `ADMIN_EMAIL` is set and no user has that email, create `role=admin` with `ADMIN_PASSWORD`, `ADMIN_NAME`, and `date_of_birth` from `ADMIN_DATE_OF_BIRTH`. That date must be 21+ in `Asia/Kolkata`, and `age_verified` is set true. If `ADMIN_EMAIL` is set and the date is missing or under 21, the process exits and does not create the user. If the email already exists, do not reset the password or the date of birth.

## 4. Session refresh and logout

```
API call returns 401
  → POST /auth/refresh once
  → success: retry the original call
  → fail: clear memory token, go to /login

Logout
  → POST /auth/logout
  → clear client session
  → go to /
```

## 5. Browse

```
Navbar: Home | Cigars | Cigarettes | Lighters | Accessories | Contact Us
Category page
  → GET /categories/{slug}/products
  → grid of ProductCard
  → filters: text query, and `origin` on every category page when the query string is present
Product page /products/{slug}
  → gallery, full specs for that category, quantity stepper, Add
Search icon
  → opens a field that navigates to /search?q=
  → GET /products?q= as already specified in `04-api-structure.md`
```

That endpoint returns an empty page when neither `q` nor `new=1` is set. `new=1` is the “view all new arrivals” list. `origin` only narrows `q` or `new=1`. Category pages use `GET /categories/{slug}/products`, which honors `origin` on its own. Every category page forwards `?origin=`, including `/cigarettes`.

Out of stock: card remains visible, Add is disabled, label “Out of stock”.

Low stock: black pill `Only {stock_qty} left` when stock is above 0. Stock 0 stays “Out of stock” and does not use that pill.

## 6. Home page

See `08-homepage.md` for sections. Data calls on `/`:

```
GET /products/featured
GET /products/new-arrivals
GET /brands
```

Hero, trust, founder note, and origin cards do not call the API.

## 7. Add to cart

```
Visitor clicks Add
  → not logged in → /login?next=/products/{slug}
  → logged in → POST /cart/items
  → cart icon count updates from GET /cart
```

Quantity stepper on the card defaults to 1. It cannot go below 1 or above `stock_qty`.

## 8. Checkout

```
/cart shows lines, subtotal, edit quantity, remove
Checkout
  → GET /checkout/summary shows subtotal, flat shipping, total
  → form: name, phone, address, city, state, postal code, notes
  → POST /orders copies those amounts onto the order
  → success page with order_number and the sentence:
       “Order placed. We confirm payment and delivery before shipping.
        This is not a completed card payment.”
  → customer can open /account/orders
```

## 9. Admin — add, edit, remove

```
/admin  (dashboard counts: published products, hidden, unread messages)
/admin/products
    table: name, category, price, stock, published, deleted
    filter: In shop | Hidden | Removed
    Removed uses `status=deleted` and is where Restore appears
    [Add product]
/admin/products/new
    form sections: basics, price & stock, specs (specs collapse based on category), ratings, flags
    save → POST /admin/products
    then image upload on the edit page
/admin/products/{id}
    PATCH to save
    upload / reorder / delete images
    [Remove product] confirms, then DELETE (soft)
    removed products show a Restore button
```

After a published product is saved, the matching category page and the home carousels show it on refresh. After remove, public pages do not show it.

Admin nav (not the store navbar):

```text
Dashboard | Products | Orders | Messages | View store | Log out
```

Orders and Messages links can render in Phase 4 as disabled or as empty states, and become real in Phase 6. Prefer real empty pages (`No orders yet`) so the layout does not change later.

## 10. Contact Us

```
/contact
  name, email, phone optional, subject, message
  → POST /contact
  → thank-you state on the same page
Admin /admin/messages
  → list, mark read, archive
```

## 11. Order status (admin)

```
/admin/orders → open order → change status along the allowed path
Customer /account/orders sees the new status on next load
```

Cancelling does not restock by itself. The admin edits `stock_qty` if the pieces go back on the shelf.

## 12. Account and password reset (Phase 8)

```
/account
  edit name and phone → PATCH /auth/me
  change password → POST /auth/change-password

/forgot-password
  email only
  → POST /auth/forgot-password
  → same success sentence whether or not the email exists

Email link → /reset-password?token=...
  → POST /auth/reset-password
  → then /login

Order placed
  → customer email with order number and total
  → admin email when ADMIN_EMAIL is set
Dev with SMTP unset: the API logs the message instead of sending it.
The log line is enough to finish the reset flow on a laptop.
```

## Flow the UI must not allow
- Register as admin
- Add to cart with a quantity above stock
- See a soft-deleted product on the storefront
- Place an order with an empty cart
- Skip the DOB check by omitting it (API requires the field)
