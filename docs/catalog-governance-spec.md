# Catalog governance (beer containers & label formats)

**Status:** Draft for ops + product  
**Applies to:** Standard label dimensions, materials, OGOS `location_code` / `material_code` mappings, HP Indigo constraints.

## 1. Source of truth

| Layer | System of record | Notes |
|-------|------------------|-------|
| **Technical catalog** | Repo + DB migration or admin API | Versioned; environments mirror semver or migration id |
| **Commercial naming** | CMS / i18n bundles | Can diverge in copy; must map 1:1 to technical IDs |
| **Supplier (OGOS)** | Optimum / OGOS master data | Our catalog **maps** to OGOS codes; we do not fork their prices silently |

## 2. Change approval flow

1. **Proposal:** ticket with rationale (margin, new machine, customer demand).
2. **Technical review:** check OGOS compatibility, preflight rules, matching dataset impact.
3. **Approval:** product owner + technical lead for material/price-affecting rows.
4. **Deploy:** migration or admin publish + **announce** version bump to support.

Emergency fix (bad dimension): **hotfix branch** + post-incident note in changelog.

## 3. Versioning

- **Catalog version:** `major.minor.patch` or monotonic integer in `catalog_version` table.
- **Breaking change** (removed ID, incompatible dimension): **major** bump; clients receive deprecation window when possible.
- **API:** responses include `catalog_version` so storefronts cache correctly.

## 4. Audit & rollback

- **Audit log table:** `who`, `when`, `old_json`, `new_json`, `reason`.
- **Rollback:** re-apply previous snapshot or run `down` migration; max SLA defined by support.
- **Read-only prod:** direct SQL edits forbidden; use admin API or migration only.

## 5. Admin UI constraints (when built)

- Cannot delete a row referenced by **open orders** in last N days; soft-delete + tombstone.
- **Price-linked fields** require re-approval if margin policy would be violated (integrate `pricing_policy` checks).

---

*Next implementation step:* `catalog_versions` + `catalog_audit_log` tables when DB model is chosen for production.
