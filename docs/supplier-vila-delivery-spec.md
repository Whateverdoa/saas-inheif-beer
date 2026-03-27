# Supplier delivery transport spec (Vila / press handoff)

**Status:** Draft for engineering lock-in  
**Schema:** `supplier_job` version `1.x` (see below)  
**Related code:** `app/services/ogos_service.py` (current OGOS OrderService path)

## 1. Purpose

Define how INHEIF hands a **confirmed label order** to production (Vila / Optimum Group stack) with **clear versioning, idempotency, retries, and failure semantics**. This doc does not replace OGOS API contracts; it layers **our** job envelope and operational rules on top.

## 2. Integration options

| Transport | When to use | Auth | Strengths | Risks |
|-----------|-------------|------|-----------|-------|
| **OGOS Order API** (existing) | Default path; pricing + submit already implemented | Bearer (`OGOS_API_KEY`) | Single integration, aligned with Optimum | Less control over bespoke multi-file bundling until API supports it |
| **HTTPS JSON + presigned file URLs** | Direct Vila/MIS endpoint if offered | mTLS or OAuth2 client credentials + short-lived tokens | Explicit schema, good for automation | Requires partner endpoint and SLA |
| **SFTP hotfolder** | Partner prefers file drop | SSH keys; optional IP allowlist | Simple for print shops | Weaker audit trail; ordering via manifest JSON mandatory |
| **Email with attachments** | Fallback / tiny volume only | SPF-aligned sender; manual triage | Zero setup for partner | No machine idempotency; not acceptable at scale |

**Default recommendation:** keep **OGOS Order API** as the production integration until multi-label submission is fully represented there; parallel **design** the `supplier_job` envelope so SFTP or HTTPS can consume the same payload.

## 3. Canonical job envelope (`supplier_job`)

All transports should carry the same logical payload (serialized as JSON for API/SFTP manifest; embedded metadata for email only as last resort).

### 3.1 Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | yes | e.g. `1.0` — bump minor for additive fields; major for breaking changes |
| `idempotency_key` | string (UUID) | yes | Stable per logical submission; see §5 |
| `source_system` | string | yes | e.g. `inheif-saas-beer` |
| `created_at` | string (RFC3339 UTC) | yes | Job creation time in our system |
| `order` | object | yes | Commercial order reference and customer-facing ids |
| `label_set` | object | yes | Multi-label bundle (MVP contract) |
| `production` | object | yes | Material, quantity, finishing, ship-to |
| `files` | array | yes | Ordered list of artifacts to transfer |

### 3.2 `order`

- `internal_order_id` (string, required): our primary key / draft id  
- `ogos_order_id` (string, optional): after OGOS submit  
- `shopify_order_gid` (string, optional): if Shopify is source of truth  
- `customer_reference` (string, optional): user-visible PO  
- `currency` (string, ISO 4217)

### 3.3 `label_set`

- `label_set_id` (string, required): groups all PDFs for one SKU  
- `roles` (array, required): each item `{ "role": "front"|"back"|"neck"|"other", "file_id": "<id>" }`  
- Policy: **front** required; others optional; each file **independently** passes preflight before submit

### 3.4 `files[]`

Each item:

- `id` (string): referenced by `label_set.roles`  
- `role` (enum): copy of role for redundancy  
- `filename` (string): e.g. `front.pdf`  
- `sha256` (string): checksum of decoded bytes  
- `byte_size` (int)  
- `uri` (string): `https://…` presigned GET or `sftp://…` path after upload  
- `preflight_status` (enum): `passed` \| `warning` \| `blocked`  
- `preflight_warnings` (string[], optional)

### 3.5 `production`

Maps to OGOS `OrderSpecifications` / partner fields:

- `location_code`, `material_code`, `quantity`, `shape`, `adhesive`, `core_size`, `product_type`, `shipping_method`  
- `shipping_address` (object, same shape as `ShippingAddress` in `ogos_service.py`)

## 4. Schema versioning

- **Format:** `MAJOR.MINOR`  
- **Minor:** additive fields only; consumers must ignore unknown keys  
- **Major:** breaking changes; deploy new consumer before producer switch; keep dual-read window if needed  
- **HTTP:** `X-Supplier-Job-Schema: 1.0` on requests  
- **SFTP:** manifest file name `supplier_job-<idempotency_key>.json` next to PDFs

## 5. Idempotency

- **Key:** UUID v4 generated once per user-confirmed submission (not per retry)  
- **HTTP:** header `Idempotency-Key: <uuid>` (same as body `idempotency_key`)  
- **Retention:** supplier stores outcomes **≥ 72 hours**; we store forever in `event_store` / orders table  
- **Semantics:** duplicate key + same body → **200/204** with original result; duplicate key + different body → **409** (we treat as bug and alert)

## 6. Retries (our client)

Aligned with `OGOSService` patterns (`MAX_ATTEMPTS = 4`, exponential backoff):

| Attempt | Backoff (approx) | Notes |
|---------|-------------------|--------|
| 1 | immediate | |
| 2 | ~0.8 s | |
| 3 | ~1.6 s | |
| 4 | ~3.2 s | After failure: surface `requires_review` to ops |

- **Retry only** on: `408`, `429`, `5xx`, network timeouts  
- **Do not retry** on: `400`, `401`, `403`, `404`, `409`, `422` (fix payload or auth first)

## 7. Failure handling

| Phase | Symptom | Action |
|-------|---------|--------|
| Pre-submit validation | Missing front PDF, checksum mismatch | 4xx to client; no supplier call |
| Transport failure after accept | Timeout unknown | Retry with idempotency key; if exhausted, mark order **stuck** and alert |
| Supplier 4xx | Bad manifest | Log payload hash; fix mapping; **new** idempotency only after root-cause |
| Supplier business reject | Artwork rejected | Map to `requires_review`; notify customer |

**Reconciliation job (batch):** daily query supplier (if API supports) for `internal_order_id` / `ogos_order_id` mismatch and heal state.

## 8. Security

- Presigned URLs: **short TTL** (15–60 min), **HTTPS only**, **single GET**  
- Secrets: never in manifest JSON; use env / vault  
- SFTP: restrict by IP + ed25519 keys; chroot per tenant if multi-tenant drops  
- PII: minimize in manifest; align with DPA and retention policy  

## 9. Open decisions (product / Vila)

- [ ] Confirm whether multi-PDF is one OGOS call or multiple (until then, `supplier_job` is source of truth for file list)  
- [ ] Confirm official Vila endpoint (REST vs hotfolder) for high volume  
- [ ] SLA and support window for failed jobs  

---

*Next implementation step:* add a small `SupplierJobV1` Pydantic model mirroring §3 and map from `OrderSubmitRequest` / future multi-label submit.
