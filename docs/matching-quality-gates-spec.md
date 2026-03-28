# Matching quality gates (format / container → catalog)

**Status:** Draft for ML + product sign-off  
**Scope:** Rules that decide when auto-matched beer-label formats are safe vs require human review.

## 1. Labeled evaluation corpus

| Requirement | Detail |
|-------------|--------|
| **Minimum size (MVP)** | ≥ 200 PDFs or label-intake records with **gold** `label_type_id` + container metadata |
| **Coverage** | Stratify by neck / body / can / sleeve; include edge cases (odd aspect ratio, multi-panel) |
| **Provenance** | Store `source`, `annotator`, `approved_at`; no anonymous gold changes in production path |
| **Versioning** | Corpus `dataset_version` pinned in CI; bump when labels change |

## 2. Accuracy targets (validation set, held-out)

| Metric | MVP gate | Stretch |
|--------|----------|---------|
| **Top-1** | ≥ 85% exact format match | ≥ 92% |
| **Top-3** | ≥ 95% gold in top-3 | ≥ 98% |
| **Abstain rate** | Documented; not a single global threshold without calibration | — |

Failing a gate **blocks** promotion of a new model or feature flag increase.

## 3. Confidence policy

- **Score source:** model softmax / calibrated margin / rule-engine confidence — must be **comparable across releases**.
- **Auto-accept:** only if `confidence >= τ_high` **and** secondary checks pass (e.g. dimensions within HP Indigo tolerance).
- **Deferred:** `τ_low <= confidence < τ_high` → return **partial** draft + `requires_review` flag.
- **Reject / manual:** `confidence < τ_low` → no auto-binding to SKU; user must pick format explicitly.

**Calibration:** set `τ_high`, `τ_low` on validation set to hit target **precision** for auto-accept (e.g. ≥ 99% precision on accepted set).

## 4. Regression tests (CI)

- **Golden set:** 30–50 fixed fixtures; **must not** change without PR review.
- **Assertions:** for each fixture, expected `top1_label_type_id` (or expected abstain).
- **Latency:** `match_ms` P95 under SLO (see handoff) on CI runner with warmed cache.

## 5. Operational logging

- Log `dataset_version`, `model_version`, `confidence`, `decision` (accept/defer/reject) per request (no raw PDF in logs).
- Weekly drift report: distribution shift vs training stratum.

---

*Owner:* Product + ML. *Next step:* freeze MVP gold set path under `tests/fixtures/label_matching/` (to be added when model exists).
