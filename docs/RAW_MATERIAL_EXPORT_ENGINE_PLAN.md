# Raw Material Master Data Export Engine Plan

**Status:** DESIGN APPROVED — Implementation Pending  
**Date:** 2026-08-18  
**Prerequisite:** Importer refactor complete (`docs/IMPORTER_REFACTOR_PLAN.md`)

---

## 1. Purpose

The Raw Material Export Engine is the inverse of the Raw Material Import Engine. It reads the current AaramBooks database state and produces Excel/CSV files that:

1. Accurately represent the current master data
2. Can be reimported with **zero changes** (all rows → IGNORED = round-trip safe)
3. Serve as snapshot backups before production migrations
4. Serve as templates for preparing updated master data files

---

## 2. Round-Trip Compatibility Requirement

The export format must be **exactly compatible** with the import format.

```
Database
    ↓
Raw Material Export Engine
    ↓
Excel file (same column headers as import template)
    ↓
Raw Material Import Engine (dry-run)
    ↓
Result: 100% IGNORED (0 CREATED, 0 UPDATED, 0 FAILED)
```

This is the **Export Round-Trip Certification Test** (future CERT-021).

---

## 3. Architecture

```
RawMaterialExportEngine (orchestrator)
        │
        ├── UOMExporter
        │     └── exports: units_of_measure table
        │
        ├── OperationalCategoryExporter
        │     └── exports: categories (RM/PKG/CON/AST roots + children only)
        │     └── excludes: Finished Goods categories
        │
        ├── SupplierExporter
        │     └── exports: masters_suppliers table
        │
        ├── RawMaterialItemExporter
        │     └── exports: products + skus (item_type = RAW_MATERIAL only)
        │
        └── BOMExporter
              └── exports: masters_boms + masters_bom_items
              └── active BOMs only (status = ACTIVE, latest version per bom_number)
              └── archived versions optionally included via --include-archived flag
```

---

## 4. Entity Exporters Design

### 4.1 UOMExporter

**Source tables:** `units_of_measure`

**Output columns (match import template exactly):**

| Column | Source Field | Notes |
|:-------|:-------------|:------|
| UoM Code | `unit_code` | Identity |
| UoM Name | `unit_name` | |
| Short Name | `short_name` | |
| Type | `unit_type` | |
| Description | `description` | |
| Status | `status` | Export even INACTIVE (preserve full state) |

**Filter:** Export all UOMs. No filter by status (full snapshot).

---

### 4.2 OperationalCategoryExporter

**Source tables:** `categories`

**Output columns (match import template exactly):**

| Column | Source Field | Notes |
|:-------|:-------------|:------|
| Category Code | `category_code` | Identity |
| Category Name | `category_name` | |
| Parent Category Code | `parent.category_code` | Join via `parent_id` |
| Description | `description` | |
| Status | `status` | |

**Filter:** 
- Export all categories where root ancestor code is in `{RM, PKG, CON, AST}` 
- Explicitly **exclude** `FG` root and all its children
- Root categories themselves (`RM`, `PKG`, `CON`, `AST`) are exported as reference rows marked `[ROOT - IMMUTABLE]` in a comment column — they cannot be imported (blocked by importer), but their presence in the export communicates the hierarchy

**Ordering:** Topological order (parents before children) — required for reimport compatibility.

---

### 4.3 SupplierExporter

**Source tables:** `masters_suppliers`

**Output columns (match import template exactly):**

| Column | Source Field | Notes |
|:-------|:-------------|:------|
| Supplier ID | `id` | Optional — present for ID-based update |
| Supplier Name | `name` | |
| Phone Number | `contact_number` | |
| GSTIN | `gstin` | |
| Email | `email` | |
| Address | `address` | |
| Remarks | `remarks` | |
| Is Job Worker | `is_job_worker` | Export as `TRUE`/`FALSE` |
| Status | `status` | |

**Filter:** Export all suppliers.

---

### 4.4 RawMaterialItemExporter

**Source tables:** `products` JOIN `skus` JOIN `pricing` JOIN `packaging` JOIN `units_of_measure` JOIN `categories`

**Output columns (match import template exactly):**

| Column | Source Field | Notes |
|:-------|:-------------|:------|
| Item Code | `skus.item_code` | Identity |
| Master Item Name | `products.product_name` | |
| Category Code | `categories.category_code` | Via products.category_id |
| Base UoM Code | `units_of_measure.unit_code` | Via skus.uom_id |
| Barcode | `skus.barcode` | |
| Description | `products.description` | |
| Status | `skus.status` | |
| Selling Price | `pricing.selling_price` | |
| MRP | `pricing.mrp` | |
| Cost Price | `pricing.cost_price` | |
| GST % | `pricing.gst_percentage` | |
| HSN Code | `pricing.hsn_code` | |
| Packaging Length (in cm) | `packaging.length` | |
| Packaging Breadth (in cm) | `packaging.breadth` | |
| Packaging Height (in cm) | `packaging.height` | |
| Packaging Weight (in kg) | `packaging.weight` | |

**Filter:** `products.item_type = RAW_MATERIAL` only. Never exports `FINISHED_GOODS`.

---

### 4.5 BOMExporter

**Source tables:** `masters_boms` JOIN `masters_bom_items` JOIN `skus` (for finished and component)

**Output columns (match import template exactly):**

| Column | Source Field | Notes |
|:-------|:-------------|:------|
| BOM Number | `masters_boms.bom_number` | Identity |
| BOM Name | `masters_boms.bom_name` | |
| Finished SKU | `skus.item_code` (target) | Via `masters_boms.sku_id` |
| Base Quantity | `masters_boms.base_quantity` | |
| Component SKU | `skus.item_code` (component) | Via `masters_bom_items.component_sku_id` |
| Component Quantity | `masters_bom_items.quantity` | |
| Wastage % | `masters_bom_items.wastage_percentage` | |
| Version | `masters_boms.version` | Informational — importer ignores, uses content-hash |
| Status | `masters_boms.status` | ACTIVE or ARCHIVED |
| Effective From | `masters_boms.effective_from` | |
| Effective To | `masters_boms.effective_to` | |

**Multi-row expansion:** Each BOM is exported as N rows (one per component). This exactly matches the import format.

**Default filter:** Active BOMs only (`status = ACTIVE`, latest version per `bom_number`).  
**Optional flag:** `--include-archived` exports all versions of all BOMs.

**BOM Version Preservation:** Export includes `Version` column. Importer ignores the version number and uses content-based matching. This is intentional — the version in the export is informational metadata.

---

## 5. Export Output Format

### Excel (Primary)

- Single workbook: `AaramBooks_RM_Export_{YYYY-MM-DD}.xlsx`
- One sheet per entity:
  - `UoM`
  - `Operational_Categories`
  - `Suppliers`
  - `Raw_Materials`
  - `BOM`
  - `Export_Metadata` (snapshot info, timestamp, row counts)

### CSV (Secondary — optional per-entity)

One CSV file per entity for lightweight exports.

---

## 6. Export Metadata Sheet

Every export workbook includes an `Export_Metadata` sheet:

| Field | Value |
|:------|:------|
| Export Date | 2026-08-18T14:30:00Z |
| Environment | development / staging / production |
| Exported By | user@aaramhomes.com |
| AaramBooks Version | 0.2.0 |
| UOM Count | 3 |
| Category Count | 12 |
| Supplier Count | 5 |
| Raw Material Count | 8 |
| Active BOM Count | 3 |
| Archived BOM Count | 1 |
| Round-Trip Safe | YES |

---

## 7. Archived/Inactive Data Handling

| Data | Default Behaviour | Override Flag |
|:-----|:-----------------|:--------------|
| INACTIVE UOMs | Included | `--active-only` excludes |
| INACTIVE Categories | Included | `--active-only` excludes |
| INACTIVE Suppliers | Included | `--active-only` excludes |
| INACTIVE Raw Materials | Included | `--active-only` excludes |
| ARCHIVED BOMs | Excluded | `--include-archived` includes |
| Non-latest BOM versions | Excluded | `--include-archived` includes all versions |

---

## 8. Export Audit Logging

Every export run is logged to the `import_audit_logs` table (same table as import):

| Field | Value |
|:------|:------|
| `operation_type` | `EXPORT` |
| `entity_type` | Entity exported (or `ALL` for full export) |
| `environment` | dev / staging / production |
| `executed_by_user_id` | User UUID or system |
| `filename` | Output filename |
| `status` | COMPLETED / FAILED |
| `counts` | JSON: `{exported: N, archived_included: M}` |

---

## 9. CLI Interface (Planned)

```bash
# Export all entities to Excel
python scripts/manage_exports.py --format excel --output exports/

# Export single entity
python scripts/manage_exports.py --entity UOM --format csv --output exports/

# Export with archived BOMs
python scripts/manage_exports.py --entity BOM --include-archived --output exports/

# Active records only
python scripts/manage_exports.py --active-only --output exports/
```

---

## 10. Implementation Phases

| Phase | Scope | Status |
|:------|:------|:------:|
| Phase 1 | UOMExporter + OperationalCategoryExporter | ⏳ Pending |
| Phase 2 | SupplierExporter + RawMaterialItemExporter | ⏳ Pending |
| Phase 3 | BOMExporter (active only) | ⏳ Pending |
| Phase 4 | BOM archived versions + `--include-archived` | ⏳ Pending |
| Phase 5 | Export Audit Logging | ⏳ Pending |
| Phase 6 | Round-Trip Certification Test (CERT-021) | ⏳ Pending |

---

> [!IMPORTANT]
> Do not implement until the importer refactor (`IMPORTER_REFACTOR_PLAN.md`) is complete and approved.
> The export engine depends on the renamed importer modules for column-name constants.
