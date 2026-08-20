# Importer Refactor Plan
## Raw Material Master Data Sub-Engine

**Status:** APPROVED PLAN — Awaiting Implementation Approval  
**Date:** 2026-08-18  
**Prerequisite:** `docs/MASTER_DATA_SUB_ENGINE_ARCHITECTURE.md` approved

---

## 1. Problem Statement

The current importer modules use generic names and contain Finished Goods assumptions that violate the approved sub-engine architecture. Specifically:

| Issue | Location | Detail |
|:------|:---------|:-------|
| Generic naming | `master_data_importer.py` → `BaseMasterDataImporter` | Name implies all domains; should remain framework-level (keep as-is) |
| Mixed domain logic | `product_sku_importer.py` → `ProductSKUImporter` | Line 97: auto-detects `ItemType.FINISHED_GOODS` based on `Sku Id` column presence — FG logic inside RM engine |
| Generic category naming | `category_importer.py` → `CategoryImporter` | Handles all categories including `FG` root protection, but is registered in RM CLI |
| CLI entity key | `manage_imports.py` — `"PRODUCT_SKU"` key | Misleading — implies any SKU, should be `"RAW_MATERIAL"` |
| FG protection inconsistency | `CategoryImporter` line 10-16 | Protects FG root, but FG governance belongs in future SKU sub-engine |

---

## 2. Modules: Current vs Future State

### 2.1 `master_data_importer.py` — NO CHANGE

**Current:** `BaseMasterDataImporter`, `ImportResult`, `ImportRowResult`, `ImportAction`  
**Action:** **Keep as-is.** This is the framework base and must remain generic.  
**Reason:** Both sub-engines (RM and future SKU) share this base class.

---

### 2.2 `category_importer.py` → `operational_category_importer.py`

**Current responsibility:** Handles ALL categories including FG root protection.

**Problem:**
- FG root (`FG` code) appears in `ROOT_CATEGORIES` dict
- This implies the RM sub-engine has knowledge of FG governance
- FG categories should be the responsibility of the future SKU sub-engine

**Required change:**
- Rename file: `category_importer.py` → `raw_material/operational_category_importer.py`
- Rename class: `CategoryImporter` → `OperationalCategoryImporter`
- Keep `ROOT_CATEGORIES` with all 5 roots (FG, RM, PKG, CON, AST) — **root protection stays here** because the RM sub-engine must reject any attempt to write to a root node it doesn't own
- Add explicit scope guard: if a parent category resolves to `FG` root, REJECT with message: `"Finished Goods categories are managed by the SKU Master Data Sub-Engine."`
- Update CLI entity key: `"CATEGORY"` → `"OPERATIONAL_CATEGORY"`

**Migration action:** Move file, rename class, add FG scope guard.

**Test impact:** `tests/data_import/test_category_importer.py` — update import paths. No logic changes.

---

### 2.3 `product_sku_importer.py` → `raw_material_item_importer.py`

**Current responsibility:** Handles both Raw Material Items AND (implicitly) Finished Goods SKUs.

**Problem (line 95-97):**
```python
# Determine ItemType implicitly based on whether it's FG Catalogue or Raw Material
# If "Sku Id" is provided, it's typically Finished Goods.
item_type = ItemType.FINISHED_GOODS if row.get("Sku Id") else ItemType.RAW_MATERIAL
```

This auto-inference of `FINISHED_GOODS` vs `RAW_MATERIAL` based on column presence means the RM importer secretly creates FG records if the input file happens to include a `Sku Id` column.

**Required change:**
- Rename file: `product_sku_importer.py` → `raw_material/raw_material_item_importer.py`
- Rename class: `ProductSKUImporter` → `RawMaterialItemImporter`
- **Remove FG auto-inference logic.** Always set `item_type = ItemType.RAW_MATERIAL`
- **Add explicit guard:** If a row contains `"Sku Id"` field with a non-empty value, REJECT with: `"Finished Goods SKUs are managed by the SKU Master Data Sub-Engine, not the Raw Material importer."`
- Update CLI entity key: `"PRODUCT_SKU"` → `"RAW_MATERIAL"`

**Migration action:** Move file, rename class, remove FG logic, add guard.

**Test impact:** `tests/data_import/test_product_sku_importer.py` — update import paths + add test for FG guard rejection.

---

### 2.4 `uom_importer.py` — MOVE ONLY

**Current responsibility:** UOM import. Clean. No FG contamination.  
**Required change:** Move to `raw_material/uom_importer.py`. Class name stays `UOMImporter`.  
**Migration action:** Move file only.

---

### 2.5 `supplier_importer.py` — MOVE ONLY

**Current responsibility:** Supplier import. Clean. No FG contamination.  
**Required change:** Move to `raw_material/supplier_importer.py`. Class name stays `SupplierImporter`.  
**Migration action:** Move file only.

---

### 2.6 `bom_importer.py` — MOVE ONLY

**Current responsibility:** BOM import. Clean. No FG contamination.  
**Required change:** Move to `raw_material/bom_importer.py`. Class name stays `BOMImporter`.  
**Migration action:** Move file only.

---

## 3. CLI Changes (`scripts/manage_imports.py`)

| Old Entity Key | New Entity Key | Reason |
|:---------------|:---------------|:-------|
| `CATEGORY` | `OPERATIONAL_CATEGORY` | Scope-specific name |
| `PRODUCT_SKU` | `RAW_MATERIAL` | Accurate domain name |
| `UOM` | `UOM` | No change |
| `SUPPLIER` | `SUPPLIER` | No change |
| `BOM` | `BOM` | No change |

Update `IMPORTERS` dict and import paths. Old entity keys can be kept as aliases during a transition window, then removed.

---

## 4. Directory Structure After Refactor

```
src/domains/data_ingestion/services/
│
├── master_data_importer.py              # Framework base — UNCHANGED
│
├── raw_material/                        # NEW DIRECTORY
│   ├── __init__.py
│   ├── uom_importer.py                  # Moved
│   ├── operational_category_importer.py # Renamed + FG guard added
│   ├── supplier_importer.py             # Moved
│   ├── raw_material_item_importer.py    # Renamed + FG logic removed
│   └── bom_importer.py                  # Moved
│
├── sku_master/                          # NEW PLACEHOLDER DIRECTORY
│   ├── __init__.py
│   └── PLACEHOLDER.md
│
└── adapters/                            # UNCHANGED (ShopDeck data ingestion)
    ├── shopdeck_order.py
    └── ...
```

---

## 5. Test File Updates Required

| Test File | Change Required |
|:----------|:----------------|
| `tests/data_import/test_uom_importer.py` | Update import path |
| `tests/data_import/test_category_importer.py` | Update import path + test FG guard |
| `tests/data_import/test_supplier_importer.py` | Update import path |
| `tests/data_import/test_product_sku_importer.py` | Update import path + add FG rejection test |
| `tests/data_import/test_bom_importer.py` | Update import path |
| `tests/data_import/test_import_engine.py` | Update import path |
| `tests/data_import/test_golden_migration.py` | Update import paths |
| `tests/data_import/fixtures/cert_fixtures.py` | Update import paths |

---

## 6. Backward Compatibility

The old module locations must NOT be silently deleted. For a transition period:

- Add a `__deprecated__.py` stub in the old location that imports from the new path and emits a `DeprecationWarning`
- This prevents immediate breakage if any external scripts reference the old paths
- Remove stubs in the next planned release after confirming all references are updated

---

## 7. Implementation Order

```
Step 1: Create raw_material/ and sku_master/ directories
Step 2: Move uom_importer.py, supplier_importer.py, bom_importer.py
Step 3: Rename + modify category_importer.py → operational_category_importer.py
Step 4: Rename + modify product_sku_importer.py → raw_material_item_importer.py
Step 5: Update CLI (manage_imports.py) imports and entity key map
Step 6: Update all test import paths
Step 7: Add deprecation stubs at old paths
Step 8: Re-run full certification suite (25 tests must pass)
Step 9: Update AI_HANDOFF.md
```

---

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|:-----|:--------:|:-----------|
| Import path breakage in test files | Low | Step 6 handles all test updates |
| CLI entity key rename breaks existing scripts | Low | Add aliases + deprecation window |
| FG logic removal breaks Raw_Materials dry-run | None | Raw_Materials sheet has no `Sku Id` column — no impact |
| Existing certified test behaviour changes | None | Only import paths change; zero logic changes in 4/5 modules |

---

> [!IMPORTANT]
> Do not implement until this plan is approved.
> The refactor must pass all 25 existing certification tests after completion.
