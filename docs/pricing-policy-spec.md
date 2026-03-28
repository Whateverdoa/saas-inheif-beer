# Pricing policy (sell price from supplier / OG cost)

**Status:** Engineering default — product must confirm percentages and floors.  
**Code:** `app/services/pricing_policy.py`

## Goals

- Compute **customer sell price** from **supplier cost (ex-VAT)** with a **target gross margin on revenue**.
- Support **B2B** (quote primarily **ex-VAT**) vs **B2C / storefront** (quote **incl-VAT**).
- Enforce **rounding**, **minimum order (ex-VAT)**, **minimum margin (€ per order)**, and **discount caps** for repeatability and audit.

## Definitions

- **Supplier cost ex-VAT** (`cost_ex_vat`): landed cost from OGOS / supplier quote, excluding VAT.
- **Target gross margin on revenue** (`target_margin`):  
  \(\text{margin} = (\text{revenue} - \text{cost}) / \text{revenue}\).  
  So **revenue ex-VAT** = \(\text{cost} / (1 - \text{target_margin})\).
- **VAT rate** (`vat_rate`): e.g. `0.21` for NL standard rate; configurable per tenant/store later.

## Rounding

- Money stored and returned as `Decimal`.
- **Round to cents** with **half-up** (`ROUND_HALF_UP`) unless a jurisdiction rule requires otherwise.

## Minimums

| Rule | Behavior |
|------|----------|
| **Minimum order (ex-VAT)** | If line/order subtotal ex-VAT is below floor, either **block checkout** or **bump to floor** — product choice; code exposes `meets_minimum_order`. |
| **Minimum margin (€)** | After pricing, ensure `(subtotal_ex_vat - cost_ex_vat) >= minimum_margin_eur`; otherwise **reject** or **lift price** to meet floor (code exposes validation helper). |

## Discount governance

- **Max discount %** (e.g. tier-based): `effective_discount = min(requested, max_allowed)`.
- Stacks: document whether promo and volume are **multiplicative** or **additive** (default: apply **one** governed discount % to ex-VAT subtotal for MVP).

## Environment / config (suggested)

| Variable | Meaning |
|----------|---------|
| `PRICING_DEFAULT_TARGET_MARGIN` | Default target margin \(0..1\), e.g. `0.35` |
| `PRICING_DEFAULT_VAT_RATE` | e.g. `0.21` |
| `PRICING_MIN_ORDER_EX_VAT_EUR` | Optional floor |
| `PRICING_MIN_MARGIN_EUR` | Optional minimum € margin per order |
| `PRICING_MAX_DISCOUNT_PCT` | Optional cap on extra discount % |

Load per-organization overrides from DB when available; env = global default.

## Shopify / storefront

- Shopify displays **inc-VAT** for consumers; use `QuotePresentation.INCL_VAT` for payloads sent to storefront helpers.
- INHEIF remains source of truth for **policy**; Shopify line items should reflect the same rounded totals after tax rules are applied.

## Open (product)

- [ ] Confirm default **target margin** by customer tier and material.
- [ ] Confirm **minimum order** is hard block vs auto-bump.
- [ ] Confirm **EU OSS / B2C VAT** rules when selling outside NL.
