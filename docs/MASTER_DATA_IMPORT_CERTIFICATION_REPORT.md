# Master Data Import Certification Report

**Project:** AaramBooks Inventory  
**Date:** 2026-08-18  
**Certified by:** Antigravity / Claude Sonnet  
**Source of Truth:** `docs/ENTITY_IMPORT_RULE_MATRIX.md`

---

## Overall Status: ✅ PRODUCTION CERTIFIED

All 25 certification tests pass. The framework is safe for staging and production use.

---

## Test Execution Summary

```
PYTHONPATH=. venv/bin/pytest tests/data_import/ -v
25 passed, 0 failed in 4.63s
```

---

## Certification Results

| CERT | Name | Behaviour Verified | Status |
|:----:|:-----|:-------------------|:------:|
| **CERT-001** | Exact Match Idempotency (UOM) | Second identical import returns IGNORED, zero duplicates in DB | ✅ PASS |
| **CERT-001** | Exact Match Idempotency (Supplier) | Second identical import returns IGNORED | ✅ PASS |
| **CERT-002** | Partial Match Update (UOM) | Name updated, unit_code (identity) unchanged | ✅ PASS |
| **CERT-002** | Partial Match Update (Supplier) | Address updated, GSTIN and name unchanged | ✅ PASS |
| **CERT-003** | Ambiguous Match Rejection | Same phone + different name+GSTIN → REJECTED, no merge | ✅ PASS |
| **CERT-004** | Supplier Identity Protection (by ID) | Non-existent Supplier ID → FAIL, no ghost record created | ✅ PASS |
| **CERT-004b** | ID-based Update Preserves UUID | Name updated, UUID identity preserved | ✅ PASS |
| **CERT-005** | UOM Type Immutable | `unit_type` change attempt → REJECTED with clear error | ✅ PASS |
| **CERT-006** | Category Root Protection | All 5 root codes (FG, RM, PKG, CON, AST) blocked from import | ✅ PASS |
| **CERT-007** | Category Hierarchy Parent Lock | Parent reassignment → REJECTED | ✅ PASS |
| **CERT-008** | Category Archive Behaviour | Status set to INACTIVE via import, FK references intact | ✅ PASS |
| **CERT-009** | Within-Batch Hierarchy Resolution | Parent created in same batch → child can reference it immediately | ✅ PASS |
| **CERT-009b** | Reversed Order Fails Cleanly | Child before parent → first row fails, second succeeds | ✅ PASS |
| **CERT-010** | SKU Barcode Immutability | Barcode change → REJECTED, DB unchanged | ✅ PASS |
| **CERT-011** | SKU Attribute Update | Price and colour updated, item_code identity preserved | ✅ PASS |
| **CERT-012** | BOM Exact Content Match → IGNORE | Same components + same qty → IGNORED even if version number differs in file | ✅ PASS |
| **CERT-013** | BOM Content Change → New Version | Changed qty → old BOM ARCHIVED, new BOM ACTIVE at version+1 | ✅ PASS |
| **CERT-014** | BOM Duplicate Component Handling | Exact duplicate component line deduplicated at app layer, no DB constraint error | ✅ PASS |
| **CERT-015** | BOM Dependency Order | BOM referencing non-existent SKU → REJECTED | ✅ PASS |
| **CERT-016** | Dry-Run Safety | No DB writes after dry-run + rollback | ✅ PASS |
| **CERT-016b** | Dry-Run Repeatability | Second dry-run after rollback still reports CREATE | ✅ PASS |
| **CERT-017** | Commit Persists Data | Committed row visible in DB | ✅ PASS |
| **CERT-017b** | Partial Failure Isolation | Valid rows written, failed rows not written | ✅ PASS |
| **CERT-019** | Full Master Initialisation | Empty DB → full 5-step init (UOM → Category → Supplier → SKU → BOM) with zero FK errors | ✅ PASS |
| **CERT-020** | Golden Migration Test | Two independent isolated DBs given identical input → identical final state | ✅ PASS |

---

## Real Dry-Run Results (Production Template)

File: `AaramBooks_Master_Data_Import_Template.xlsx`

| Entity | Sheet | Records | Created | Failed | Result |
|:-------|:------|--------:|--------:|-------:|:-------|
| UOM | UoM | 3 | 3 | 0 | ✅ CLEAN |
| Category | Categories | 12 | 12 | 0 | ✅ CLEAN (with within-batch parent resolution) |
| Supplier | Suppliers | 3 | 3 | 0 | ✅ CLEAN |
| Product/SKU | Raw_Materials | 1 | 1 | 0 | ✅ CLEAN |
| BOM | BOM | 2 | 0 | 2 | ✅ EXPECTED FAIL (SKU dependencies not in template) |

The BOM failure is **correct behaviour** — it enforces CERT-015 (dependency order). BOMs can only be imported after their component SKUs exist in the database.

---

## Governance Decisions (Frozen)

| Decision | Rule |
|:---------|:-----|
| **Barcode** | Permanently immutable via import. Any change attempt is REJECTED. An admin override mechanism (outside the import framework) must be created separately if needed. |
| **Finished Goods Sub-Categories** | Can be created via `CategoryImporter`. Root-level categories (FG, RM, PKG, CON, AST) are permanently protected. |
| **UOM Type** | `unit_type` is immutable once set. Attempting to change INTEGER → DECIMAL is rejected. |
| **Supplier Phone** | No UNIQUE constraint at DB level. Duplicate phone detection is at application layer to allow legitimate cases. |
| **BOM Versioning** | Content-based. The version number in the import file is ignored — only actual component changes trigger a new version. |
| **SKU Identity** | `item_code`, `sku_code`, `barcode` — all permanently immutable via import. |

---

## Files Delivered

```
src/domains/data_ingestion/services/
  ├── master_data_importer.py     # BaseMasterDataImporter, ImportResult
  ├── uom_importer.py             # CERT-001, CERT-002, CERT-005
  ├── category_importer.py        # CERT-006, CERT-007, CERT-008, CERT-009
  ├── supplier_importer.py        # CERT-001, CERT-002, CERT-003, CERT-004
  ├── product_sku_importer.py     # CERT-010, CERT-011
  └── bom_importer.py             # CERT-012, CERT-013, CERT-014, CERT-015

scripts/
  └── manage_imports.py           # CLI: --entity --file --sheet --commit --env --user

tests/data_import/
  ├── fixtures/cert_fixtures.py
  ├── test_uom_importer.py        # CERT-001, CERT-002, CERT-005
  ├── test_category_importer.py   # CERT-006, CERT-007, CERT-008, CERT-009
  ├── test_supplier_importer.py   # CERT-001, CERT-002, CERT-003, CERT-004
  ├── test_product_sku_importer.py # CERT-010, CERT-011
  ├── test_bom_importer.py        # CERT-012, CERT-013, CERT-014, CERT-015
  ├── test_import_engine.py       # CERT-016, CERT-017
  └── test_golden_migration.py    # CERT-019, CERT-020
```

---

## How to Run Production Import

```bash
# Step 1: Always dry-run first
python scripts/manage_imports.py --entity UOM      --file path/to/master.xlsx --sheet UoM       --env staging
python scripts/manage_imports.py --entity CATEGORY --file path/to/master.xlsx --sheet Categories --env staging
python scripts/manage_imports.py --entity SUPPLIER --file path/to/master.xlsx --sheet Suppliers  --env staging
python scripts/manage_imports.py --entity PRODUCT_SKU --file path/to/master.xlsx --sheet Raw_Materials --env staging
python scripts/manage_imports.py --entity BOM      --file path/to/master.xlsx --sheet BOM       --env staging

# Step 2: Review reports — confirm 0 FAILED, 0 AMBIGUOUS

# Step 3: Commit in order (respects dependency chain)
python scripts/manage_imports.py --entity UOM         ... --commit --env production
python scripts/manage_imports.py --entity CATEGORY    ... --commit --env production
python scripts/manage_imports.py --entity SUPPLIER    ... --commit --env production
python scripts/manage_imports.py --entity PRODUCT_SKU ... --commit --env production
python scripts/manage_imports.py --entity BOM         ... --commit --env production
```

---

*This document is the official certification record for the AaramBooks Master Data Import Framework.*
