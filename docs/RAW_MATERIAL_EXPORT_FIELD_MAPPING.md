# Raw Material Export — Field Mapping Specification

**Date:** 2026-08-18  
**Status:** APPROVED FOR IMPLEMENTATION  
**Derived from:** Live importer code + DB model inspection  
**Prerequisite:** `docs/RAW_MATERIAL_EXPORT_ENGINE_PLAN.md`

> **Round-Trip Contract:** Every exported file must be re-importable with 100% IGNORED result (zero CREATED, zero UPDATED, zero FAILED). This document is the authoritative specification that guarantees that contract per entity.

---

## Terminology

| Term | Meaning |
|:-----|:--------|
| **DB Column** | Actual SQLAlchemy model attribute name |
| **DB Table** | SQLAlchemy `__tablename__` |
| **Export Column** | Column header written to the Excel/CSV output |
| **Import Column** | Column header expected by the importer (must match export column exactly for round-trip) |
| **Identity Field** | Field used to match records during import; immutable after creation |
| **Mutable Field** | Field that the importer will UPDATE on PARTIAL MATCH |
| **Protected Field** | Field the importer reads but refuses to change after creation |
| **Omitted Field** | DB field that has no export column (internal, audit, or FK) |

---

## BaseModel Fields — Handling Across All Entities

Every model inherits from `BaseModel` which adds:

| DB Column | Type | Export? | Reason |
|:----------|:-----|:-------:|:-------|
| `id` | UUID | ✅ Supplier only | Suppliers use ID-based identity matching |
| `created_on` | DateTime | ❌ | Internal audit — not importable |
| `updated_on` | DateTime | ❌ | Internal audit — not importable |
| `created_by` | UUID | ❌ | System-managed |
| `updated_by` | UUID | ❌ | System-managed |

---

## Entity 1 — Unit of Measure (UOM)

### Source
- **Table:** `units_of_measure`
- **Model:** `UnitOfMeasureModel`
- **Importer:** `UOMImporter`

### Field Mapping

| DB Column | DB Type | Export Column | Required in Import | Classification | Notes |
|:----------|:--------|:--------------|:----------------:|:--------------|:------|
| `unit_code` | String(50) | `UoM Code` | ✅ | **Identity** | Exact string match. Unique constraint. |
| `unit_name` | String(100) | `UoM Name` | ✅ | Mutable | Updated on PARTIAL MATCH |
| `short_name` | String(20) | `Short Name` | ✅ | Mutable | Updated on PARTIAL MATCH |
| `description` | String(255) | `Description` | ❌ | Mutable | NULL-safe (empty string accepted) |
| `unit_type` | String(20) | `Type` | ✅ | **Protected** | `INTEGER` or `DECIMAL`. Immutable after creation — change attempt → FAIL |
| `status` | GenericStatus | `Status` | ❌ | Mutable | `ACTIVE` or `INACTIVE`. Defaults to `ACTIVE` on import |
| `id` | UUID | *(omitted)* | — | Omitted | Internal PK |

### Exact Match Comparison Fields
The importer compares: `unit_name` + `short_name` + `description` + `status`  
`unit_type` is read but not compared (immutability guard fires first).

### Inactive/Archived Handling
- **INACTIVE UOMs:** Exported with `Status = INACTIVE`. Importer will IGNORE (exact match) or UPDATE if something else changed.
- **No "archived" state** for UOM — only ACTIVE / INACTIVE.
- **Export default:** All UOMs exported regardless of status.

### Round-Trip Guarantee
Export produces `Status` as `ACTIVE` or `INACTIVE`. Importer accepts both. ✅

---

## Entity 2 — Operational Categories

### Source
- **Table:** `categories`
- **Model:** `CategoryModel`
- **Importer:** `CategoryImporter` (future: `OperationalCategoryImporter`)

### Scope Filter
Export only categories where the root ancestor code is in `{RM, PKG, CON, AST}`.  
Explicitly **exclude** `FG` root and all descendants.

### Field Mapping

| DB Column | DB Type | Export Column | Required in Import | Classification | Notes |
|:----------|:--------|:--------------|:----------------:|:--------------|:------|
| `category_code` | String(50) | `Category Code` | ✅ | **Identity** | Unique. Immutable after creation. |
| `category_name` | String(100) | `Category Name` | ✅ | Mutable | Updated on PARTIAL MATCH |
| `description` | String(255) | `Description` | ❌ | Mutable | NULL-safe |
| `status` | GenericStatus | `Status` | ❌ | Mutable | `ACTIVE` or `INACTIVE` |
| `parent_id` | UUID FK | *(resolved)* | — | **Protected** | Not exported as UUID. Resolved to code below. |
| `parent.category_code` | String(50) | `Parent Category Code` | ❌ | **Protected** | Exported as the parent's `category_code`. Cannot be changed once set. |
| `item_type` | ItemType | *(omitted)* | — | Omitted | Internal classification. Not used by importer (category scope guard handles it). |
| `display_order` | Integer | *(omitted)* | — | Omitted | Not used by importer. |
| `id` | UUID | *(omitted)* | — | Omitted | Internal PK |

### Hierarchy Handling & Export Modes

**Export ordering is critical for round-trip safety.** Parent rows must appear before child rows.

We define two export modes to satisfy both machine round-tripping and human readability without breaking constraints:

#### MODE 1 — RESTORE EXPORT (DEFAULT)
**Purpose:** Database backup / restore / round-trip certification
**Rules:**
- Export ONLY importer-compatible rows (operational child categories, items, suppliers, BOMs).
- **EXCLUDE immutable root category rows** (`RM`, `PKG`, `CON`, `AST`).
- Reason: Root categories already exist and cannot be recreated/imported. The round-trip contract requires that the machine export does not contain rows that are intentionally guaranteed to fail import.

#### MODE 2 — DOCUMENTATION EXPORT
**Purpose:** Human-readable hierarchy report.
**Rules:**
- Include the immutable root categories for visual completeness.
- These files are **NOT intended for import**.

Algorithm (for processing):
1. Fetch all operational categories (RM/PKG/CON/AST roots + descendants).
2. Build a topological sort: process categories with `parent_id = NULL` first (level 0), then their children (level 1), recursively.
3. In Restore Mode (default), filter out the level 0 root rows.

### Inactive/Archived Handling
- `INACTIVE` categories are exported with `Status = INACTIVE`.
- Children of inactive categories are still exported (they retain their own status independently).
- On reimport, an INACTIVE parent being re-created via import is impossible (root protection / parent must exist check); children pointing to INACTIVE parents will resolve correctly since the parent still exists in DB.

### Round-Trip Guarantee
Restore Export mode omits root rows → no expected FAILs → importer processes all rows → ✅

---

## Entity 3 — Suppliers

### Source
- **Table:** `masters_suppliers`
- **Model:** `Supplier`
- **Importer:** `SupplierImporter`

### Field Mapping

| DB Column | DB Type | Export Column | Required in Import | Classification | Notes |
|:----------|:--------|:--------------|:----------------:|:--------------|:------|
| `id` | UUID | `Supplier ID` | ❌ | **Identity (primary)** | Exported always. Enables ID-based update — strongest identity signal. |
| `name` | String(255) | `Supplier Name` | ✅ | **Identity (secondary)** + Mutable | Part of secondary matching. Also a mutable field if update occurs. |
| `gstin` | String(15) | `GSTIN` | ❌ | **Identity (secondary)** + Mutable | Used in ambiguity detection and matching. |
| `contact_number` | String(50) | `Phone Number` | ❌ | **Identity (secondary)** + Mutable | Used in ambiguity detection. |
| `email` | String(255) | `Email` | ❌ | Mutable | Updated on PARTIAL MATCH |
| `address` | Text | `Address` | ❌ | Mutable | Updated on PARTIAL MATCH |
| `remarks` | Text | `Remarks` | ❌ | Mutable | Updated on PARTIAL MATCH |
| `is_job_worker` | Boolean | `Is Job Worker` | ❌ | **Protected** | Exported as `TRUE`/`FALSE`. Importer reads it but does NOT update it after creation (requires operational validation). |
| `status` | *(absent)* | *(omitted)* | — | Omitted | `Supplier` model has no status column. All exported suppliers are active. |

### Exact Match Comparison Fields
The importer compares: `name` + `contact_number` + `gstin` + `email` + `address` + `remarks` + `is_job_worker`

### Ambiguity Detection (Must be preserved in export)
The exporter must always include `Supplier ID` in the output. This ensures reimport uses ID-based matching (strongest signal) and avoids the ambiguity detection path entirely.

### Inactive/Archived Handling
- The `Supplier` model has **no status column**. There is no ACTIVE/INACTIVE distinction.
- Export: all suppliers unconditionally.
- Future: if a status column is added, revisit this section.

### Round-Trip Guarantee
With `Supplier ID` always exported → importer uses ID-based matching → exact match → IGNORED ✅

---

## Entity 4 — Raw Material Items

### Source
- **Tables:** `products` + `skus` + `pricing` + `packaging` + `categories` + `units_of_measure`
- **Models:** `ProductModel`, `SKUModel`, `PricingModel`, `PackagingModel`
- **Importer:** `ProductSKUImporter` (future: `RawMaterialItemImporter`)

### Scope Filter
Export only: `products.item_type = 'RAW_MATERIAL'`  
Never export `FINISHED_GOODS` products.

### Field Mapping

| DB Column | DB Table | Export Column | Required in Import | Classification | Notes |
|:----------|:---------|:--------------|:----------------:|:--------------|:------|
| `skus.item_code` | skus | `Item Code` | ✅ | **Identity** | Primary identity. Unique. Immutable. |
| `skus.sku_code` | skus | *(omitted)* | — | **Identity** | For Raw Materials, `sku_code` is always NULL or equals `item_code`. Not a separate import column. |
| `products.product_code` | products | *(omitted)* | — | **Identity** | For Raw Materials, auto-derived as = `item_code` (1:1 mapping). Not exported separately. |
| `skus.barcode` | skus | `Barcode` | ❌ | **Identity** + Protected | Exported if present. Immutable after creation — change attempt → FAIL. |
| `products.product_name` | products | `Master Item Name` | ✅ | Mutable | Maps to product name |
| `products.description` | products | `Description` | ❌ | Mutable | NULL-safe |
| `products.brand` | products | `attr_Brand` | ❌ | Mutable | Maps to brand field |
| `skus.size` | skus | `Size` | ❌ | Mutable | NULL-safe |
| `skus.color` | skus | `Colour` | ❌ | Mutable | NULL-safe |
| `categories.category_code` | categories | `Category Code` | ❌ | **Protected** | Exported as category code (FK resolved). Cannot be changed via import after creation. |
| `units_of_measure.unit_code` | units_of_measure | `Base UoM Code` | ❌ | **Protected** | Exported as UOM code (FK resolved). Cannot be changed via import after creation. |
| `skus.status` | skus | `Status` | ❌ | Mutable | `ACTIVE` or `INACTIVE` |
| `pricing.selling_price` | pricing | `Selling Price` | ❌ | Mutable | `0.0` if no pricing record |
| `pricing.mrp` | pricing | `MRP` | ❌ | Mutable | `0.0` if no pricing record |
| `pricing.cost_price` | pricing | `Cost Price` | ❌ | Mutable | `0.0` if no pricing record |
| `pricing.gst_percentage` | pricing | `GST %` | ❌ | Mutable | `0.0` if no pricing record |
| `pricing.hsn_code` | pricing | `HSN Code` | ❌ | Mutable | NULL-safe |
| `packaging.length` | packaging | `Packaging Length (in cm)` | ❌ | Mutable | `0.0` if no packaging record |
| `packaging.breadth` | packaging | `Packaging Breadth (in cm)` | ❌ | Mutable | `0.0` if no packaging record |
| `packaging.height` | packaging | `Packaging Height (in cm)` | ❌ | Mutable | `0.0` if no packaging record |
| `packaging.weight` | packaging | `Packaging Weight (in kg)` | ❌ | Mutable | `0.0` if no packaging record |

### Omitted DB Fields (Not Exported)

| DB Column | Reason |
|:----------|:-------|
| `skus.id` | Internal PK — not used by importer |
| `products.id` | Internal PK |
| `skus.product_id` | FK resolved via product_code |
| `skus.uom_id` | Resolved to `Base UoM Code` |
| `products.category_id` | Resolved to `Category Code` |
| `skus.attribute_values` | JSON blob — not in import template |
| `skus.pattern`, `material`, `thread_count` | Not in import template |
| `products.product_type` | Not in import template |
| `products.item_type` | Always `RAW_MATERIAL` — implicit in RM sub-engine |

### Exact Match Comparison Fields (importer)
`size`, `color`, `status`, `selling_price`, `mrp`, `cost_price`, `gst_percentage`, `length`, `breadth`, `height`, `weight`

### Note on `Sku Id` Column
The export must **never** include a `Sku Id` column. Its presence triggers the FG boundary guard → FAIL.

### Inactive/Archived Handling
- INACTIVE items exported with `Status = INACTIVE`.
- No archived concept for items — only ACTIVE/INACTIVE.

### Round-Trip Guarantee
`Item Code` (identity) → exact match → importer IGNOREs ✅  
`Category Code` and `Base UoM Code` are protected → not updated on re-import ✅  
Zero `Sku Id` column in export → no FG guard triggered ✅

---

## Entity 5 — Bill of Materials (BOM)

### Source
- **Tables:** `masters_boms` + `masters_bom_items` + `skus` (target and component)
- **Models:** `BOMModel`, `BOMItemModel`
- **Importer:** `BOMImporter`

### Scope Filter
**Default export:** `status = 'ACTIVE'` BOMs only (latest version per `bom_number`).  
**With `--include-archived`:** All BOMs, all versions.

### Multi-Row Expansion
Each BOM is N rows in the file (one row per component). This exactly mirrors the import format.

### Field Mapping — BOM Header Fields (repeated per component row)

| DB Column | DB Table | Export Column | Required in Import | Classification | Notes |
|:----------|:---------|:--------------|:----------------:|:--------------|:------|
| `bom_number` | masters_boms | `BOM Number` | ✅ | **Identity** | Groups rows into one BOM. Repeated for each component row. |
| `bom_name` | masters_boms | `BOM Name` | ❌ | Mutable | NULL-safe. Repeated per row. |
| `target_sku.item_code` | skus (join) | `Finished SKU` | ✅ | **Identity** | Resolved from `target_item_id` FK → `skus.item_code`. |
| `target_quantity` | masters_boms | `Base Quantity` | ❌ | **Content** | Part of content hash. Integer. Defaults to 1. |
| `version` | masters_boms | `Version` | ❌ | Informational | Exported for human reference only. **Importer ignores this field** — versioning is content-based. |
| `status` | masters_boms | `BOM Status` | ❌ | Informational | `ACTIVE` or `ARCHIVED`. Exported for reference. Importer creates new version or ignores based on content. |
| `effective_from` | masters_boms | `Effective From` | ❌ | Informational | ISO date. Human reference only — importer sets this at creation time. |
| `effective_to` | masters_boms | `Effective To` | ❌ | Informational | ISO date. `NULL` for active. Human reference only. |

### Field Mapping — BOM Component Fields (one row per component)

| DB Column | DB Table | Export Column | Required in Import | Classification | Notes |
|:----------|:---------|:--------------|:----------------:|:--------------|:------|
| `component_sku.item_code` | skus (join) | `Component SKU` | ✅ | **Content** | Resolved from `component_item_id` FK → `skus.item_code`. |
| `quantity` | masters_bom_items | `Component Quantity` | ✅ | **Content** | Part of content hash. Numeric(10,4). |
| `wastage_percentage` | masters_bom_items | `Wastage %` | ❌ | **Content** | Part of content hash. Numeric(5,2). Defaults to 0.0. |
| `tolerance_percentage` | masters_bom_items | `Tolerance %` | ❌ | **Content** | Not currently part of content hash in importer. Numeric(5,2). |
| `uom.unit_code` | units_of_measure | `Component UOM` | ❌ | **Content** | Resolved from `uom_id` FK → `unit_code`. If NULL, importer falls back to component SKU's base UOM. |

### Omitted DB Fields (Not Exported)

| DB Column | Reason |
|:----------|:-------|
| `masters_boms.id` | Internal PK |
| `masters_bom_items.id` | Internal PK |
| `masters_boms.target_item_id` | FK → resolved to `Finished SKU` |
| `masters_bom_items.bom_id` | FK — grouped by `BOM Number` |
| `masters_bom_items.component_item_id` | FK → resolved to `Component SKU` |
| `masters_bom_items.unit_of_measure` | Legacy string field (always "-"). Not used by importer. |

### BOM Version Handling

| Scenario | Export Behaviour | Import Behaviour |
|:---------|:-----------------|:----------------|
| Active BOM (latest version) | Always exported | Content match → IGNORED ✅ |
| Archived BOM (old version) | Only with `--include-archived` | Always IGNORED (content matches old version, but active is newer) |
| Two versions in same export | Version column distinguishes them (informational) | Only active content checked → IGNORED ✅ |

### Exact Content Hash Fields (determines versioning)
`target_item_id` + `target_quantity` + for each component: (`component_item_id` + `quantity` + `wastage_percentage` + `uom_id`)

`tolerance_percentage` is **not** currently part of the content hash (per importer source at line 141). Export includes it for completeness — no round-trip impact.

### Round-Trip Guarantee
Active BOM exported → re-imported → content matches exactly → IGNORED ✅  
Component rows deduplicated before export (no exact duplicates) ✅  
`Version` column is informational — importer does not use it → no false NEW VERSION created ✅

---

## Export Column Summary Table

A consolidated view of all export column headers in each sheet:

### Sheet: `UoM`
```
UoM Code | UoM Name | Short Name | Type | Description | Status
```

### Sheet: `Operational_Categories`
```
Category Code | Category Name | Parent Category Code | Description | Status | Export Note
```

### Sheet: `Suppliers`
```
Supplier ID | Supplier Name | Phone Number | GSTIN | Email | Address | Remarks | Is Job Worker
```

### Sheet: `Raw_Materials`
```
Item Code | Master Item Name | Category Code | Base UoM Code | Barcode | attr_Brand |
Size | Colour | Description | Status |
Selling Price | MRP | Cost Price | GST % | HSN Code |
Packaging Length (in cm) | Packaging Breadth (in cm) | Packaging Height (in cm) | Packaging Weight (in kg)
```

### Sheet: `BOM`
```
BOM Number | BOM Name | Finished SKU | Base Quantity | Version | BOM Status | Effective From | Effective To |
Component SKU | Component Quantity | Wastage % | Tolerance % | Component UOM
```

### Sheet: `Export_Metadata`
Every export must include format versioning metadata for future compatibility control.

```
Export Format Version | Export Date | Environment | Exported By | AaramBooks Version |
UOM Count | Category Count | Supplier Count | Raw Material Count |
Active BOM Count | Archived BOM Count (if included) | Round-Trip Safe
```
**Example Export Format Version:** `RM_MASTER_EXPORT_V1`


---

## Null / Empty Value Handling

| Scenario | Export Behaviour | Import Behaviour |
|:---------|:-----------------|:----------------|
| `NULL` optional string | Export as empty string `""` | Importer reads as `""` — matches DB `NULL` via `(existing.field or "") == exported_value` |
| `NULL` numeric (pricing/packaging) | Export as `0` | Importer reads as `0.0` via `_safe_float()` — matches |
| `NULL` UUID FK | Export resolved code as empty string | Importer ignores blank category/UOM codes |
| `FALSE` boolean | Export as `FALSE` | Importer reads `FALSE` correctly via `strip().upper() in ["TRUE","YES","1","Y"]` |

---

## CERT-021 — Export Round-Trip Certification Test Specification

```
Given:
  A populated development database (UOM, Categories, Suppliers, Raw Materials, BOMs)

Steps:
  1. Run export → produces Excel file
  2. Run import (dry-run) against same database from the exported file
  3. Assert: 0 CREATED, 0 UPDATED, 0 FAILED (AMBIGUOUS = 0)
  4. Assert: IGNORED count = number of non-root rows exported
  5. Exception: root category rows (RM, PKG, CON, AST) always FAIL → expected

Pass Criteria:
  - All non-root rows → IGNORED
  - All root category rows → FAILED (expected — root protection)
  - Zero unexpected failures
```

---

*This document is the authoritative field-level specification for the Raw Material Export Engine.*  
*No exporter code has been written yet. Implementation follows approval of this document.*
