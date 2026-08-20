# Category Migration Analysis
## AaramBooks Development Database — Category Structure Discovery

**Date:** 2026-08-18  
**Status:** READ-ONLY ANALYSIS — No database changes made  
**Database:** `test_inventory.db`

---

## 1. Current Category Tree

### Task 2 Finding: CASE B — Encoded ShopDeck Paths (NOT True Hierarchy)

All 8 categories have `parent_id = NULL`. There is no true parent-child tree. Every category is a flat root-level node. The apparent "hierarchy" in category names is ShopDeck's taxonomy path encoded as a double-underscore-separated string stored in a single field.

```
[FLAT STRUCTURE — ALL 8 CATEGORIES ARE ROOT-LEVEL]

CAT-554EC7   Uncategorized                                       (21 SKUs)
CAT-C09415   home__home_furnishing__bed_linen                    (12 SKUs)
CAT-C9CF4C   home__home_furnishing__cushions_covers               (1 SKU)
CAT-80FB12   home__home_improvement__utility                     (27 SKUs)
CAT-79C3D3   kids_baby__home_dcor__bedsheets                      (1 SKU)
CAT-5BDD44   others_68c015dd317e68f10e190e4c__others__bedsheets   (1 SKU)
CAT-354017   others_68c015dd317e68f10e190e4c__others__cushions    (1 SKU)
CAT-DC3EE5   others_68c015dd317e68f10e190e4c__others__kids_dohar  (1 SKU)
```

**No category has a parent.** The `parent_id` column is NULL for every row.

### Category Metadata Table

| Code | Name | Parent | Status | SKU Count |
|:-----|:-----|:-------|:-------|----------:|
| CAT-554EC7 | Uncategorized | — | ACTIVE | **21** |
| CAT-C09415 | home__home_furnishing__bed_linen | — | ACTIVE | 12 |
| CAT-80FB12 | home__home_improvement__utility | — | ACTIVE | 27 |
| CAT-C9CF4C | home__home_furnishing__cushions_covers | — | ACTIVE | 1 |
| CAT-79C3D3 | kids_baby__home_dcor__bedsheets | — | ACTIVE | 1 |
| CAT-5BDD44 | others_68c015dd317e68f10e190e4c__others__bedsheets | — | ACTIVE | 1 |
| CAT-354017 | others_68c015dd317e68f10e190e4c__others__cushions | — | ACTIVE | 1 |
| CAT-DC3EE5 | others_68c015dd317e68f10e190e4c__others__kids_dohar | — | ACTIVE | 1 |

**Total: 65 SKUs across 8 flat categories. 0 uncategorized (all have a category_id).**

---

## 2. Hierarchy Assessment (Task 2)

**Verdict: CASE B — Encoded ShopDeck Taxonomy Paths**

The category names are ShopDeck's internal navigation paths, structured as:
```
<level_1>__<level_2>__<leaf>
```

Decoded path examples:

| Raw Name | L1 | L2 | L3 |
|:---------|:---|:---|:---|
| `home__home_furnishing__bed_linen` | Home | Home Furnishing | Bed Linen |
| `home__home_furnishing__cushions_covers` | Home | Home Furnishing | Cushion Covers |
| `home__home_improvement__utility` | Home | Home Improvement | Utility |
| `kids_baby__home_dcor__bedsheets` | Kids & Baby | Home Décor | Bedsheets |
| `others_68c015dd317e68f10e190e4c__others__bedsheets` | Others (ShopDeck internal ID) | Others | Bedsheets |
| `others_68c015dd317e68f10e190e4c__others__cushions` | Others (ShopDeck internal ID) | Others | Cushions |
| `others_68c015dd317e68f10e190e4c__others__kids_dohar` | Others (ShopDeck internal ID) | Others | Kids Dohar |

The `others_68c015dd317e68f10e190e4c` segment contains a raw ShopDeck internal category UUID — not a business name.

---

## 3. SKU–Category Mapping Analysis (Task 3)

### SKUs with Active Inventory Movements (13 SKUs)

These are the most operationally sensitive SKUs. Their `category_id` must not be changed without careful consideration.

| SKU Code | Movements | Category | Net Stock |
|:---------|----------:|:---------|----------:|
| KD-AL-IG-KDB | 6 | home__home_improvement__utility | +101 |
| KD-MDB-MGLD-SK | 4 | others__bedsheets | +99 |
| AH-PINKRAINBOW-BD-4060 | 3 | kids_baby__home_dcor__bedsheets | +15 |
| TLS-STRP-RB-DWB | 1 | home__home_improvement__utility | +130 |
| TLS-STRP-CS-DWB | 1 | home__home_improvement__utility | +100 |
| TLS-BB-GEO-QDB | 1 | home__home_improvement__utility | +5 |
| AH-BBDOHAR-CAR-JSS-4060 | 1 | others__kids_dohar | +11 |
| AH-RUBY-JS-KDB | 1 | Uncategorized | -1 |
| AH-TERRACOTTA-FRLK-KDB-5PC | 1 | home__home_furnishing__bed_linen | -1 |
| KD-RJ-RJP-KDB | 1 | home__home_improvement__utility | -1 |
| AH-BLUEBLSM-KDCH-SK | 1 | home__home_furnishing__bed_linen | -1 |
| AH-OTTO-YELLOW-HS | 1 | home__home_improvement__utility | -1 |
| KD-IK-BLUSH-KDB | 1 | home__home_improvement__utility | -1 |

### SKUs Without Categories
**None** — all 65 SKUs have a `category_id`. However, 21 SKUs are in the `Uncategorized` bucket which is a ShopDeck fallback, not a real business category.

### SKUs in Suspect Categories
- **27 SKUs** in `home__home_improvement__utility` — This is clearly a catch-all/misassignment. Products here include bedsheets, comforter sets, mattress covers, diwan sets, and ottoman stools. The name does not accurately describe these products.
- **21 SKUs** in `Uncategorized` — No business classification at all.

### Product-Level Business Classification (from product names)

By analysing product names, the actual business taxonomy is:

| Business Product Type | Count | Current ShopDeck Category |
|:----------------------|------:|:--------------------------|
| Bedsheets (King/Queen/Double) | ~35 | home__home_furnishing__bed_linen, home__home_improvement__utility, Uncategorized |
| Cushion Covers | ~6 | home__home_furnishing__cushions_covers, Uncategorized, others__cushions |
| Kids Dohar / Baby Blankets | ~3 | others__kids_dohar, kids_baby__home_dcor__bedsheets |
| Comforter / Bedding Sets | ~5 | home__home_improvement__utility, Uncategorized |
| Mattress Protectors | ~5 | home__home_improvement__utility |
| Diwan Bedsheet Sets | ~4 | home__home_improvement__utility |
| Ottoman Stools | ~3 | home__home_improvement__utility |
| Apron | ~1 | Uncategorized |

---

## 4. ShopDeck vs AaramBooks Category Governance Comparison (Task 4)

### Approved AaramBooks Root Categories
```
FG  — Finished Goods   (immutable root)
RM  — Raw Materials    (immutable root)
PKG — Packaging        (immutable root)
CON — Consumables      (immutable root)
AST — Assets           (immutable root)
```

### Compliance Assessment

| # | Current Category | Compliant? | Issue |
|:--|:-----------------|:----------:|:------|
| 1 | Uncategorized | ❌ | Not under any AaramBooks root |
| 2 | home__home_furnishing__bed_linen | ❌ | ShopDeck path, not under FG root |
| 3 | home__home_furnishing__cushions_covers | ❌ | ShopDeck path, not under FG root |
| 4 | home__home_improvement__utility | ❌ | ShopDeck path — misclassified products |
| 5 | kids_baby__home_dcor__bedsheets | ❌ | ShopDeck path, not under FG root |
| 6 | others_68c...others__bedsheets | ❌ | ShopDeck internal UUID in name |
| 7 | others_68c...others__cushions | ❌ | ShopDeck internal UUID in name |
| 8 | others_68c...others__kids_dohar | ❌ | ShopDeck internal UUID in name |

**None of the current 8 categories comply with the AaramBooks category governance.**

**No AaramBooks root categories (FG, RM, PKG, CON, AST) exist in the database.**

---

## 5. Finished Goods Special Analysis (Task 5)

### Current State
All 65 SKUs are `item_type = FINISHED_GOODS` with ShopDeck-derived flat categories.

### Natural Business Taxonomy (derived from product names)

```
Finished Goods (FG)
│
├── Home Linen
│     ├── Bedsheets
│     │     ├── King Size Bedsheets          (~18 SKUs)
│     │     ├── Super King Size Bedsheets    (~4 SKUs)
│     │     ├── Queen/Double Bedsheets       (~5 SKUs)
│     │     └── Bedsheet Sets (with cushions)(~8 SKUs)
│     ├── Comforter Sets                     (~5 SKUs)
│     └── Dohar / Baby Blankets              (~3 SKUs)
│
├── Cushion Covers
│     └── Cushion Cover Sets                 (~6 SKUs)
│
├── Home Utility
│     ├── Mattress Protectors                (~5 SKUs)
│     ├── Diwan Sets                         (~4 SKUs)
│     └── Ottoman Stools                     (~3 SKUs)
│
└── Kids / Baby
      └── Kids Bedsheets & Dohar            (~3 SKUs)
```

**Recommendation: Option A — Keep and Normalise**

> Reasoning: All existing SKUs are real business products. They have inventory movements and packer events. Creating a new parallel hierarchy and migrating `category_id` references is operationally safe (category is not referenced by inventory movements or packer events — verified below in Task 7). However, creating a completely new taxonomy from scratch risks losing the implicit groupings that ShopDeck paths encoded. The safest path is to **normalise the existing ShopDeck paths into an AaramBooks-compliant hierarchy** by:
> 1. Creating the AaramBooks root `FG` category
> 2. Creating normalised sub-categories under `FG`
> 3. Re-pointing `products.category_id` to the new categories
> 4. Archiving the ShopDeck-derived categories

---

## 6. Category Code Recommendations (Task 6)

### New Proposed AaramBooks Category Hierarchy

| Current ShopDeck Category | Proposed Code | Proposed Name | Parent Code |
|:--------------------------|:--------------|:--------------|:------------|
| *(root — does not exist)* | `FG` | Finished Goods | — |
| `home__home_furnishing__bed_linen` | `FG-HL` | Home Linen | `FG` |
| `home__home_improvement__utility` (bedsheets portion) | `FG-HL-BS` | Bedsheets | `FG-HL` |
| *(new)* | `FG-HL-CS` | Comforter Sets | `FG-HL` |
| `others_68c...others__kids_dohar` + `kids_baby__home_dcor__bedsheets` | `FG-HL-DH` | Kids Dohar & Baby Blankets | `FG-HL` |
| `home__home_furnishing__cushions_covers` + `others_68c...others__cushions` | `FG-CC` | Cushion Covers | `FG` |
| `home__home_improvement__utility` (mattress + diwan) | `FG-HU` | Home Utility | `FG` |
| *(new — Ottoman Stools)* | `FG-HU-OT` | Ottoman Stools | `FG-HU` |
| *(new — Mattress Protectors)* | `FG-HU-MP` | Mattress Protectors | `FG-HU` |
| *(new — Diwan Sets)* | `FG-HU-DW` | Diwan Sets | `FG-HU` |
| `Uncategorized` (bedsheets) | → merge into `FG-HL-BS` | — | — |
| `Uncategorized` (apron) | `FG-HU-AP` | Aprons | `FG-HU` |

### SKU Migration Mapping (Proposed)

| Current Category | → New Category | SKUs to Migrate |
|:-----------------|:---------------|----------------:|
| home__home_furnishing__bed_linen | FG-HL-BS | 12 |
| home__home_improvement__utility | FG-HL-BS + FG-HU-MP + FG-HU-DW + FG-HU-OT | 27 (split) |
| home__home_furnishing__cushions_covers | FG-CC | 1 |
| kids_baby__home_dcor__bedsheets | FG-HL-DH | 1 |
| others_68c...bedsheets | FG-HL-BS | 1 |
| others_68c...cushions | FG-CC | 1 |
| others_68c...kids_dohar | FG-HL-DH | 1 |
| Uncategorized | FG-HL-BS + FG-HU-AP + FG-HL-DH | 21 (split by type) |

> [!NOTE]
> The `home__home_improvement__utility` category (27 SKUs) requires **manual per-SKU classification** because it contains 4 different product types (bedsheets, mattress protectors, diwan sets, ottoman stools). This cannot be migrated as a bulk operation.

---

## 7. Migration Risk Analysis (Task 7)

### Is `category_id` referenced by inventory movements or packer events?

| Table | References category_id? | Impact of category change |
|:------|:-----------------------:|:--------------------------|
| `inventory_movements` | **No** — references `sku_id` and `warehouse_id` | ✅ Zero impact |
| `packer_events` | **No** — references `event_id`, `order_id`, `awb` | ✅ Zero impact |
| `inventory_balances` | **No** — references `sku_id` and `warehouse_id` | ✅ Zero impact |
| `operations_sales_orders` | **No** — references `sku_id` | ✅ Zero impact |
| `skus` | **No** — `category_id` is on `products`, not `skus` | ✅ Zero impact |

**Confirmed: Changing `products.category_id` has no impact on inventory movements, packer events, SKU identity, or historical data.**

### Risks Summary

| Risk | Severity | Mitigation |
|:-----|:--------:|:-----------|
| Manual classification required for 27 `home__home_improvement__utility` SKUs | **Medium** | Must be done per-SKU by business owner |
| 21 `Uncategorized` SKUs need classification | **Medium** | Business owner must classify each |
| ShopDeck category path no longer available for reconciliation after archive | **Low** | Archive (not delete) old categories |
| Reporting currently uses ShopDeck category names | **Low** | All reports will improve with proper names |
| `FG` root category does not exist yet | **Low** | Must be created first before sub-categories |

---

## 8. Proposed Migration Steps (Future — Awaiting Approval)

> [!IMPORTANT]
> **DO NOT execute these steps until approved.**

```
Step 1: Run pending Alembic migration (creates import_audit_logs table)
         → PYTHONPATH=. venv/bin/alembic stamp <prev-head>
         → PYTHONPATH=. venv/bin/alembic upgrade head

Step 2: Run UOM import (DRY RUN → COMMIT)
         → 3 UOM records

Step 3: Create AaramBooks root categories via CategoryImporter (COMMIT)
         FG, RM, PKG, CON, AST
         (These are blocked from CategoryImporter — need seeding script or direct insert)

Step 4: Create FG sub-category hierarchy via CategoryImporter (COMMIT)
         FG-HL, FG-HL-BS, FG-HL-CS, FG-HL-DH, FG-CC, FG-HU, FG-HU-MP, FG-HU-DW, FG-HU-OT

Step 5: Run Supplier import (DRY RUN → COMMIT)
         3 real suppliers

Step 6: Per-SKU category re-assignment (manual script — NOT the importer)
         Migrate products.category_id for all 65 SKUs
         This requires human classification of the 27 "utility" and 21 "Uncategorized" SKUs

Step 7: Archive ShopDeck-derived categories
         Set status = INACTIVE on all 8 original categories

Step 8: Run packer integration certification
         Verify existing 9 packer events + 26 movements unaffected

Step 9: Begin Golden Certification
```

---

## Summary

| Finding | Value |
|:--------|:------|
| Current category structure | **Flat (Case B) — ShopDeck encoded paths** |
| AaramBooks root categories in DB | **0 of 5** |
| Compliant categories | **0 of 8** |
| SKUs with inventory movements | **13** |
| SKUs requiring manual reclassification | **48** (21 Uncategorized + 27 in mixed "utility") |
| SKUs safe to bulk-migrate | **17** (clear 1:1 mapping to new categories) |
| Inventory/packer data at risk | **None — category_id not referenced** |
| Recommended migration strategy | **Option A: Normalise existing data** |

---

*This document is analysis only. No database changes have been made.*  
*Awaiting approval before any migration steps are executed.*
