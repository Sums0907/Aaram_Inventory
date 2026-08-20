# AaramBooks Master Data Import/Export Framework
## Sub-Engine Architecture Design Document

**Status:** APPROVED ARCHITECTURE — Awaiting Implementation  
**Date:** 2026-08-18  
**Supersedes:** Generic "Master Data Importer" design

---

## 1. Purpose

AaramBooks manages two fundamentally different domains of master data that have different ownership, governance, lifecycle, and source-of-truth models:

| Domain | Owner | Source of Truth | Update Trigger |
|:-------|:------|:----------------|:---------------|
| Raw Material Master Data | AaramBooks operations team | AaramBooks internal | Manual import from Excel/CSV |
| Finished Goods (SKU) Master Data | ShopDeck Catalogue | ShopDeck Master Catalogue CSV | ShopDeck catalogue sync |

Mixing these two domains inside a single generic importer creates architectural drift. A change to FG catalogue logic must not touch RM import logic, and vice versa. The sub-engine architecture enforces this separation at the code level.

---

## 2. Framework Structure

```
AaramBooks Master Data Import/Export Framework
│
│   Common capabilities (foundation layer):
│   - File parsing (Excel / CSV)
│   - Column mapping / normalization
│   - Identity matching (Exact / Partial / Ambiguous / No Match)
│   - Dry-run execution
│   - Diff generation
│   - Transaction handling
│   - Audit logging
│   - Import/Export reporting
│   - BaseMasterDataImporter (abstract base class)
│
├── Raw Material Master Data Import/Export Sub-Engine
│   │   (CURRENT SCOPE — IMPLEMENTED)
│   │
│   ├── UOMImporter
│   ├── OperationalCategoryImporter   [rename from CategoryImporter]
│   ├── SupplierImporter
│   ├── RawMaterialItemImporter       [rename from ProductSKUImporter, RM scope only]
│   └── BOMImporter
│
└── SKU Master Data Import/Export Sub-Engine
        (FUTURE SCOPE — NOT YET IMPLEMENTED)

        ├── FGCategoryImporter        [Finished Goods taxonomy only]
        ├── SKUCatalogueImporter      [FG SKUs from ShopDeck CSV]
        └── ShopDeckSyncEngine        [ShopDeck catalogue synchronization]
```

---

## 3. Framework Responsibilities (Common Layer)

These capabilities live in `src/domains/data_ingestion/services/master_data_importer.py` and are shared by **both** sub-engines:

| Capability | Description |
|:-----------|:------------|
| `BaseMasterDataImporter` | Abstract base class with `import_data(data, is_dry_run)` interface |
| `ImportAction` | Enum: CREATED / UPDATED / IGNORED / FAILED / AMBIGUOUS |
| `ImportRowResult` | Per-row outcome with identifier, action, and errors |
| `ImportResult` | Batch summary with counts and is_successful property |
| Identity Resolution Protocol | EXACT → IGNORE, PARTIAL → UPDATE, NO MATCH → CREATE, AMBIGUOUS → REJECT |
| Dry-Run Guarantee | `is_dry_run=True` never calls `session.flush()` |
| Transaction Boundary | Caller controls commit/rollback — importer only flushes within-transaction |

This layer is **technology infrastructure**, not business logic. It must remain generic.

---

## 4. Raw Material Master Data Sub-Engine

### 4.1 Scope

Controls all **AaramBooks-managed operational master data** — entities whose lifecycle is decided entirely within AaramBooks, independent of any external catalogue.

**Entities in scope:**

| Entity | Importer | Status |
|:-------|:---------|:------:|
| Unit of Measure | `UOMImporter` | ✅ Implemented |
| Operational Categories (RM / PKG / CON / AST) | `OperationalCategoryImporter` | ✅ Implemented (rename pending) |
| Suppliers | `SupplierImporter` | ✅ Implemented |
| Raw Material Items | `RawMaterialItemImporter` | ✅ Implemented (rename pending) |
| Bill of Materials | `BOMImporter` | ✅ Implemented |

**Entities explicitly excluded:**
- Finished Goods categories
- Finished Goods SKUs
- Finished Goods catalogue attributes

### 4.2 Ownership Model

```
AaramBooks Operations Team
        ↓
    Excel / CSV file
        ↓
    Raw Material Master Data Import Sub-Engine
        ↓
    AaramBooks Database
        ↓
    Raw Material Master Data Export Sub-Engine
        ↓
    Excel / CSV file (round-trip compatible)
```

### 4.3 CLI Entry Point

`scripts/manage_imports.py --entity [UOM|CATEGORY|SUPPLIER|RAW_MATERIAL|BOM]`

Post-rename, the `PRODUCT_SKU` entity key becomes `RAW_MATERIAL`.

### 4.4 Export Design (Planned — see `RAW_MATERIAL_EXPORT_ENGINE_PLAN.md`)

The export engine is the inverse of the import engine. It reads from the database and produces Excel/CSV files that are fully round-trip compatible with the importer.

---

## 5. SKU Master Data Sub-Engine (Future)

### 5.1 Scope

Controls **ShopDeck-originated Finished Goods catalogue data** — entities whose source of truth is the ShopDeck Master Catalogue, not internal AaramBooks decisions.

**Entities in scope (future):**

| Entity | Importer | Status |
|:-------|:---------|:------:|
| Finished Goods root + sub-categories | `FGCategoryImporter` | ⏳ Future |
| Finished Goods SKUs (from ShopDeck CSV) | `SKUCatalogueImporter` | ⏳ Future |
| ShopDeck taxonomy synchronization | `ShopDeckSyncEngine` | ⏳ Future |

### 5.2 Ownership Model

```
ShopDeck Master Catalogue
        ↓
    ShopDeck CSV export
        ↓
    SKU Master Data Import Sub-Engine
        ↓
    AaramBooks Database (FG domain only)
```

### 5.3 Governance

- Finished Goods categories are **NOT managed by the RM Sub-Engine**
- FG SKU creation requires a ShopDeck catalogue entry as prerequisite
- Manual FG SKU creation without a ShopDeck reference is controlled separately
- The FG Sub-Engine will enforce ShopDeck taxonomy alignment

---

## 6. Ownership Model Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                   AaramBooks Database                           │
│                                                                 │
│  AaramBooks-Controlled              ShopDeck-Controlled         │
│  ─────────────────────────          ──────────────────────────  │
│  Unit of Measure                    Finished Goods Categories   │
│  Suppliers (all types)              Finished Goods SKUs         │
│  Raw Material Categories            FG SKU Attributes           │
│  Packaging Categories               FG Catalogue Hierarchy      │
│  Consumable Categories                                          │
│  Asset Categories                                               │
│  Raw Material Items                                             │
│  Bill of Materials                                              │
│                                                                 │
│        ↑                                    ↑                   │
│  Raw Material                         SKU Master Data           │
│  Sub-Engine                           Sub-Engine (Future)       │
└─────────────────────────────────────────────────────────────────┘

---

## 7. Category Ownership Resolution

`CategoryModel.item_type` is NOT a reliable ownership indicator and MUST NEVER be used for domain classification. Historical data contains incorrect values (e.g., operational categories marked as FINISHED_GOODS).

Category ownership is determined ONLY through **category hierarchy traversal** using `category_code`.

Immutable root categories determine the domain:
- `FG` = Finished Goods (FINISHED_GOODS domain)
- `RM` = Raw Materials (OPERATIONAL domain)
- `PKG` = Packaging (OPERATIONAL domain)
- `CON` = Consumables (OPERATIONAL domain)
- `AST` = Assets (OPERATIONAL domain)

A reusable service `CategoryOwnershipResolver` handles this traversal. All import/export sub-engines must use this resolver to validate scope and determine domain ownership.
```

---

## 7. File Layout (Post-Refactor)

```
src/domains/data_ingestion/services/
│
│   ── Framework (Common Layer) ──────────────────────────────────
├── master_data_importer.py          # BaseMasterDataImporter, ImportResult, etc.
│
│   ── Raw Material Sub-Engine ───────────────────────────────────
├── raw_material/
│   ├── __init__.py
│   ├── uom_importer.py
│   ├── operational_category_importer.py   [was: category_importer.py]
│   ├── supplier_importer.py
│   ├── raw_material_item_importer.py      [was: product_sku_importer.py, RM only]
│   └── bom_importer.py
│
│   ── SKU Master Sub-Engine (Future) ─────────────────────────────
└── sku_master/
    ├── __init__.py                        [placeholder]
    └── PLACEHOLDER.md                     [scope and boundary doc]
```

---

## 8. Key Invariants

1. `master_data_importer.py` (framework base) must remain entity-agnostic.
2. `raw_material/` sub-engine must contain zero Finished Goods logic.
3. `sku_master/` sub-engine must contain zero Raw Material logic.
4. The CLI (`manage_imports.py`) routes to the correct sub-engine by entity type.
5. Round-trip compatibility is required: Export → Import must produce IGNORED for all rows (exact match).
6. Both sub-engines share the same audit logging infrastructure.
