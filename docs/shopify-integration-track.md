# Shopify.dev integration track

**Status:** Architecture draft — pick one path per environment  
**Principle:** Shopify owns **commerce UX**; INHEIF owns **preflight, matching, pricing, supplier job**.

## 1. App shape (choose one primary)

| Option | Fit | Auth | Notes |
|--------|-----|------|-------|
| **Embedded app** (Admin) | B2B brewers managing drafts | Session token via App Bridge | Fastest for “configure label inside Shopify Admin” |
| **Customer-facing** (Theme app extension + app proxy) | B2C on Online Store 2.0 | Customer Account API / legacy customer | PDF upload on storefront via app proxy to INHEIF |
| **Headless (Hydrogen / custom)** | Strong branded UX | Shopify OAuth + Storefront API | INHEIF as separate API; Shopify checkout via Cart API |

**MVP recommendation:** **Embedded app** for operator workflow + **Checkout extension or post-purchase** webhook for confirmed orders — add storefront upload in phase 2.

## 2. Session & security

- **Shopify session:** OAuth install; store `shop`, `access_token` encrypted (Shopify Partners app config).
- **INHEIF API:** HMAC or JWT from app backend → INHEIF; **no** Shopify secret in browser calling INHEIF directly for privileged ops.
- **Scopes:** minimal (e.g. `read_orders`, `write_orders` only if needed for fulfillment metadata).

## 3. Webhooks (contract sketch)

| Topic | Use |
|-------|-----|
| `orders/paid` or `orders/create` + financial status | Trigger `supplier_job` assembly when payment confirmed |
| `app/uninstalled` | Revoke tokens, disable shop mapping |
| `customers/data_request` etc. | GDPR — documented erasure path |

Payload enrichment: include **INHEIF `label_set_id`** in order note attributes or metafields at draft time.

## 4. Phased plan

| Phase | Deliverable |
|-------|-------------|
| **P0** | Read-only: link from Shopify to INHEIF hosted flow (deep link + shop param) |
| **P1** | Embedded app: create draft in INHEIF, store metafields on order |
| **P2** | Webhooks → automated supplier handoff per `supplier-vila-delivery-spec.md` |
| **P3** | Native PDF upload on storefront (app proxy + presigned uploads) |

## 5. Open decisions

- [ ] **B2B vs B2C** first: Admin embedded vs Theme extension.
- [ ] **Markets / tax:** how Shopify tax lines map to `QuotePresentation` (ex vs incl VAT).
- [ ] **Polar / Stripe:** keep existing gateways vs Shopify Payments only for label SKUs.

---

*Reference:* [Shopify app development](https://shopify.dev/docs/apps) — refresh OAuth and webhook signing on each major API version upgrade.
