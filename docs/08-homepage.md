# 08 — Home Page

Source: screenshots of [theslowdraw.com](https://theslowdraw.com/) taken 23 Nov 2026, plus that site’s section order. This document specifies **our** page. Copy below is original. Do not paste the reference site’s headlines, founder biography, company registration, addresses, or authorisation lines into the UI.

Route: `/`  
Chrome: store layout from Phase 2 (announcement, navbar, footer). Phase 3 fills the middle.

Background: `paper`. Content width: about 1120–1200px centered. Section vertical rhythm: generous, closer to 72–96px between bands than to a dense dashboard.

## Page order

| # | Section | Data | Phase |
|---|---------|------|--------|
| 1 | Announcement bar | Static | 2 (chrome) |
| 2 | Navbar | Static links | 2 |
| 3 | Hero | Static slides | 3 |
| 4 | Trust row | Static | 3 |
| 5 | Brands we carry | `GET /brands` | 3 |
| 6 | Founder’s selection | `GET /products/featured` | 3 |
| 7 | A note from the shop | Static | 3 |
| 8 | Origins | Static cards: four cigar countries, plus Denmark and Belgium for cigarettes | 3 |
| 9 | New arrivals | `GET /products/new-arrivals` | 3 |
| 10 | Make your own sampler | Static teaser until Phase 7 | 7 |
| 11 | Gift packs | Static teaser until Phase 7 | 7 |
| 12 | Partners | Omitted until we have real partners | 7 |
| 13 | Footer + statutory warning | Static | 2 |

Phases 3 ships sections 3–9. Sections 10–11 may be a single quiet line (“Sampler packs and gift packs are coming.”) so the scroll does not pretend those builders exist. Do not build the five-slot sampler UI in Phase 3.

---

## 1. Announcement bar
Thin strip, centered, two lines, gold small-caps tracking:

```text
AUTHENTIC IMPORTED STOCK  ·  DELIVERY ACROSS INDIA WHERE LAWFUL
ADULTS 21+  ·  DUTY-PAID GOODS ONLY
```

Right side: `Login` pill (outline). When a session exists, the pill says the first name and links to `/account` (customer) or `/admin` (admin).

## 2. Navbar
Left: script wordmark **Ash & Cedar** linking to `/`.

Center, uppercase, small, letterspaced:

```text
Home    Cigars    Cigarettes    Lighters    Accessories    Contact Us
```

`Home` is the current page style (slightly stronger weight) when the path is `/`.

Right: search icon (opens a field, then `/search?q=`), account icon (`/account` when logged in, `/login` when not), cart icon with a count badge when the logged-in cart has items. Cart count is hidden for logged-out visitors (badge empty, icon still links to `/cart`, which then asks them to log in).

No mega-menu in v1. The reference site’s “New to cigars / Curated collection / Bespoke sampler” dropdowns are replaced by the six labels above. That is intentional.

## 3. Hero
Two columns on desktop. One column on a narrow viewport (copy first, image second).

**Left**
- Eyebrow, small gold tracking: `IMPORTED CIGARS, CIGARETTES & ACCESSORIES`
- Headline, large serif, ink:

```text
THE RIGHT HOUR
for a good
CIGAR
```

`for a good` is the script face, gold, sitting on its own line between the two serif lines. This is the same *pattern* as the reference (serif + one script word), with different words.

- Line under the headline: `Age-verified delivery. 21+ only.`
- Slide 1 buttons:
  - Filled ink: `Shop cigars` → `/cigars`
  - Outline: `Lighters & accessories` → `/accessories`

**Right**
A large photo of cigars or a still life the business owns. Phase 3 may use a neutral placeholder in `web/public/home/` (solid paper + a simple illustration is fine) until real photography exists. Do not download the reference site’s hero photo.

**Carousel**
Three slides, dots and arrows like the screenshot. Slide copy:

| Slide | Eyebrow | Headline pattern | Buttons |
|-------|---------|------------------|---------|
| 1 | Imported cigars | The right hour / for a good / cigar | `Shop cigars` → `/cigars`, `Lighters & accessories` → `/accessories` |
| 2 | Cigarettes | Packs chosen / for the / drawer | One filled button: `Shop cigarettes` → `/cigarettes` |
| 3 | The tools | Cutters, ashtrays / and a / flame | `Shop accessories` → `/accessories`, `Shop lighters` → `/lighters` |

Auto-advance every 7 seconds. Pause on hover. Dots show the active slide.

## 4. Trust row
Six cards, three per row on desktop, one per row on a phone. White fill, hairline gold border, large radius, small icon in a circle.

| Title | Body |
|-------|------|
| Shipping across India | Discreet packing. We ship only where the sale is lawful. |
| Clear pricing | The price on the card is the price you pay for that unit. |
| Looked-after stock | Cigars are kept in controlled storage before they ship. |
| Account checkout | Orders are placed from a verified 21+ account. |
| 21+ only | We do not sell to anyone under 21. |
| Named sources | Products list the brand and origin the admin entered. |

The reference cards say “GST-compliant billing”, “secured payments”, and “100% authentic & duty-paid / authorised channels”. We do not show those sentences until the matching capability exists (real GST invoices, a payment provider, and real authorisations). The table above is the honest v1 set.

## 5. Brands we carry
Centered gold eyebrow `BRANDS WE CARRY`, then one line: `Names on the shelf right now.`

Then a horizontal row of brand names in a serif or small-caps face, divided by faint vertical rules. Source: `GET /brands`. If the list is empty, hide the whole section. Do not draw third-party logos we do not have files for. Text wordmarks are enough and avoid trademark artwork.

## 6. Founder’s selection
Eyebrow `FOUNDER'S SELECTION`.

Headline, serif, centered:

```text
NOT EVERY CIGAR.
ONLY THE ONES WE STOCK.
```

Subcopy, centered, max about 60 characters per line:

```text
A short list marked by the shop. Rank, price, and format
come from the product record — not from a slogan.
```

Then a horizontal carousel of cigar `ProductCard`s from `GET /products/featured` (published cigars only). Arrow button on the right edge. If there are no founder picks, hide the carousel and show: `The founder’s list is empty. It will show here once an admin marks products.`

### Product card (cigars) — match the screenshot anatomy
White card, soft shadow, radius.

**Top cluster, overlapping the photo**
- Circle: `#1` and tiny `FOUNDER'S PICK` when `founder_rank` is set
- Circle per visible rating: score, and the source name in tiny type (`Cigar Aficionado`, `Cigar Journal`, …)
- Text button `+N more ratings` when `extra_ratings_count > 0` (does not need a popup in v1; the detail page lists them all)
- Black pill at the top right of the photo when `low_stock`: `Only {stock_qty} left`

**Photo** of the primary image, object-contain, tall.

**Meta**
- Tiny tracked category line: brand or subtype in small caps (`HABANOS` is only allowed if the admin typed a subtype/brand that says so — display `brand` in small caps, not a hard-coded “Habanos Cigars”)
- Product name, serif
- Price, `₹5,803` style (`en-IN` grouping, no paise when the value is whole rupees)
- Quiet line: `Price is for one unit.`
- Spec grid, two columns, labels in tiny tracking:

| Left | Right |
|------|--------|
| Smoking time `75–90 min` | Intensity as 5 dots, filled = `intensity` |
| Strength, title case (`Medium to full`) | Shape, title case |
| Size | `Box of 25` and box price, when those fields exist |

Hide a row if both cells are null.

**Actions**
- Stepper `−  1  +`
- Ink pill `Add` with a cart icon

From Phase 5, Add follows `05-flows.md`: logged-out visitors go to login, and logged-in visitors post to the cart. Phase 2 and Phase 3 show the same button disabled, with the sentence `Sign in to add — cart opens in a later phase.` Those phases must not call `POST /cart/items`.

### Cards for the other departments
New-arrivals may mix categories. Use the same shell and **drop spec rows that do not apply**:

| Category | Extra lines |
|----------|-------------|
| Cigarettes | Strength, `Pack of {units_per_pack}`, origin label |
| Lighters | `origin_label` (example `Made in USA`), subtype (`Torch`) |
| Accessories | subtype (`Cutter`, `Ashtray`), one-line `short_description` |

## 7. A note from the shop
Two columns.

**Left:** a portrait frame with a warm background. Until there is a real photo, use a solid ink/gold monogram `A&C`. Do not use the reference founder’s photograph or name.

**Right:**
- Eyebrow `A NOTE FROM THE SHOP`
- One short paragraph, original, no borrowed biography. Default copy:

```text
Ash & Cedar is a shop for people who already know they want
a proper cigar, a specific cigarette, or a tool that works.
We list what we can actually ship, with the format and the
price on the card. If you want help choosing, write to us.
```

- Sign-off in the script face: `Ash & Cedar`
- Small caps: `THE SHOP`
- Outline button: `Write to the shop` → `/contact`

No “book a call”, no awards, no social proof we have not earned. Those can be added in `brand.ts` later when they are true.

## 8. Origins
Eyebrow `ORIGINS`.

Headline: `From the places they were made.`

Subcopy: `Four cigar countries, plus two cigarette origins.`

Six cards, always shown, even when that country has no published products. The category empty state handles a zero result. Do not imply we are an authorised agent of that country’s industry body.

| Card | Kind | Link |
|------|------|------|
| Cuba | Cigar origin | `/cigars?origin=Cuba` |
| Dominican Republic | Cigar origin | `/cigars?origin=Dominican%20Republic` |
| Nicaragua | Cigar origin | `/cigars?origin=Nicaragua` |
| Honduras | Cigar origin | `/cigars?origin=Honduras` |
| Denmark | Cigarette origin | `/cigarettes?origin=Denmark` |
| Belgium | Cigarette origin | `/cigarettes?origin=Belgium` |

Each card: a simple flag (emoji or inline SVG), the country name, and a one-line note we write ourselves (Cuba example: `The classic island formats.`). Denmark and Belgium are labeled as cigarette origins, not cigar valleys. Button label: `Explore {country}`.

Mexico and the USA are not home-page cards. A product with that `origin_country` still appears on its category page and in search.

## 9. New arrivals
Eyebrow `JUST ARRIVED`.

Headline: `New on the shelf.`

Subcopy: `The latest published products marked as new arrivals.`

Carousel from `GET /products/new-arrivals`, same cards as section 6, mixed categories. Centered outline button under the row: `View all new arrivals` → `/search?new=1`.

`GET /products?new=1` is specified in `04-api-structure.md`. Phase 2 implements it. Phase 3 adds the button. An empty search with neither `q` nor `new=1` stays an empty page.

Empty state: hide the carousel, keep the headline, body text `Nothing is marked as new yet.`

## 10. Sampler (Phase 7)
Reference: “Make your own sampler”, five slots, complimentary cutter, steps Pick five / Check your total / Go to checkout.

When built, it is a separate route `/sampler`, and the home section is a summary with `Build your sampler`. The rules (five cigars as separate lines, and the `include_as_sampler_cutter` flag) live in `phases/07-merchandising.md`. Do not invent a free product in the database before Phase 7.

## 11. Gift packs (Phase 7)
Reference: three cigars and two accessories, wrapped, card message. Home section is a teaser linking to `/gift-packs`. Not part of Phases 1–6.

## 12. Partners (Phase 7)
The dark brown band (“trusted by leading companies”, hotel logos) stays **out** until the business has permission to show those names. No placeholder hotel logos.

## 13. Footer
Implemented in Phase 2 so every page shares it. Repeated here so the home scroll is complete.

**Top:** script wordmark, one-line description: `Imported cigars, cigarettes, lighters, and accessories for adults 21 and older.`

**Link columns** (labels only; targets can be stubs until the feature exists):

| Cigars & more | Accessories | Help | Account | Legal |
|---------------|-------------|------|---------|--------|
| Cigars | Lighters | Contact Us | Login | Privacy |
| Cigarettes | Cutters (link `/accessories?subtype=cutter`) | Shipping note on Contact | Register | Terms |
| All new arrivals | Ashtrays (`subtype=ashtray`) | | Account | Age & tobacco |

Subtype query on accessories is optional in Phase 2. If it is not ready, both cutter and ashtray links go to `/accessories`.

**Bottom strip**
- `Buy only if you are 21 or older.`
- No fake grievance officer. When the business has a named contact, add it via `brand.ts` (`grievanceName`, `grievanceEmail`, `grievancePhone`). If those strings are empty, hide the grievance block.
- Red-bordered warning box, red text, centered:

```text
STATUTORY WARNING
TOBACCO SMOKING IS INJURIOUS TO HEALTH. SALE TO PERSONS UNDER 18
IS PROHIBITED UNDER THE COTPA ACT 2003.

OUR HOUSE POLICY
ASH & CEDAR SELLS ONLY TO ADULTS AGED 21 AND ABOVE.
```

- `© {year} Ash & Cedar. All rights reserved.`
- Buttons: Site map (a simple list of the main routes), Terms (stub)

A WhatsApp floating button is **off** until `brand.ts` has a real phone number. Do not copy the reference number.

## Responsive notes
- Hero stacks. Headline size drops but stays serif.
- Trust cards: 1 column, then 2, then 3.
- Product carousels scroll horizontally with the arrow. On a phone, one card and a peek of the next.
- Navbar: below 960px, the six links collapse into a menu button. Login and cart stay visible.
- Admin is not part of this page.

## Done when (for the home page itself)
- A person can read every core section without horizontal page scroll on a 1280px-wide window
- Featured and new-arrival cards render from the API
- Empty API results show the empty copy in this document, not a broken layout
- No sentence on the page claims an authorisation, a GST invoice, or a celebrity founder we do not have
