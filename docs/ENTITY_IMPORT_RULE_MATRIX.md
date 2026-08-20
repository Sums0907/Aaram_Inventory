# Entity Import Rule Matrix

This document defines the strict governance rules for the **AaramBooks Master Data Import/Export Framework**.

> **Architecture Note:** This framework contains two domain-specific sub-engines. Rules in this document are organised by sub-engine ownership. See `docs/MASTER_DATA_SUB_ENGINE_ARCHITECTURE.md` for the full architectural context.

---

## General Rules (All Entities, All Sub-Engines)

- **EXACT MATCH:** Ignore record. No action taken.
- **PARTIAL MATCH:** Apply entity-specific update rules (see below).
- **NO MATCH:** Create new record.
- **AMBIGUOUS MATCH:** Reject row. Manual review required.
- **NO SILENT MERGES:** Never silently merge uncertain records.
- **DRY RUN:** All operations are non-destructive until `--commit` is passed. Dry-run must never flush to the database.

---

# Raw Material Master Data Sub-Engine

**Controller:** AaramBooks operations team  
**Source of Truth:** AaramBooks internal (Excel/CSV prepared by team)  
**CLI:** `python scripts/manage_imports.py --entity [UOM|OPERATIONAL_CATEGORY|SUPPLIER|RAW_MATERIAL|BOM]`

---

## 1. Supplier

- **Immutable Identity:** Internal Supplier ID (if provided).
- **Mutable Fields:** GSTIN, Name, Phone Number, Email, Address, Remarks.
- **Protected Fields:** Is Job Worker (requires operational validation before change).
- **Matching Priority:** 1. Supplier ID (if provided). 2. GSTIN + Name + Phone (controlled secondary matching).
- **Ambiguous Match Rule:** If phone number matches but name AND GSTIN are completely different → REJECT.
- **Constraints:** Phone number and GSTIN are NOT unique constraints in the database. Ambiguous detection is at application layer.

---

## 2. Unit of Measure (UOM)

- **Immutable Identity:** UOM Code.
- **Mutable Fields:** UOM Name, Short Name, Description, Status.
- **Protected Fields:** `unit_type` (INTEGER vs DECIMAL) — attempting to change triggers FAIL with explicit message.
- **Matching Priority:** 1. UOM Code (exact string match).

---

## 3. Operational Categories

**Applies to:** Root ancestors: `RM`, `PKG`, `CON`, `AST` and all their descendants.  
**Controlled by:** AaramBooks  
**Sub-Engine:** Raw Material Master Data Sub-Engine

> [!IMPORTANT]
> `CategoryModel.item_type` must never be used for domain classification. Hierarchy traversal is the sole authoritative source of truth.

- **Immutable Identity:** Category Code.
- **Mutable Fields:** Category Name, Description, Status.
- **Protected Fields:** Parent Category Code. Once a parent is set, it cannot be changed via import.
- **Root Protection:** The 5 root categories (`FG`, `RM`, `PKG`, `CON`, `AST`) are IMMUTABLE. They cannot be renamed, created, deleted, archived, or reparented via any import.
- **FG Scope Guard:** If a category's parent resolves to the `FG` root (via hierarchy traversal), the `OperationalCategoryImporter` REJECTS the row.
- **Within-Batch Resolution:** A parent category created earlier in the same import batch can immediately be referenced as a parent by later rows.
- **Ownership:** 1 SKU belongs to exactly 1 category. Attributes belong to SKUs/Items, not to Categories.
- **Archiving:** Setting `Status = INACTIVE` archives a category. This does not cascade to child categories or assigned SKUs.

---

## 4. Raw Material Items

**Applies to:** Raw Material items (`item_type = RAW_MATERIAL`) only.  
**Controlled by:** AaramBooks  
**Sub-Engine:** Raw Material Master Data Sub-Engine

> [!IMPORTANT]
> **Finished Goods SKUs are NOT handled by this importer.**  
> If a row contains a non-empty `Sku Id` field (the ShopDeck FG identifier), the `RawMaterialItemImporter` REJECTS it with: `"Finished Goods SKUs are managed by the SKU Master Data Sub-Engine, not the Raw Material importer."`

- **Immutable Identity:** Item Code (primary), Barcode, Product Code.
- **Mutable Fields:** Name, Size, Colour, Attributes, Selling Price, MRP, Cost Price, GST %, HSN Code, Packaging dimensions, Status.
- **Protected Fields:** Category ID, UOM ID — cannot be changed via import after initial assignment.
- **Rules:** Never allow changing identity codes. To correct an identity code, create a new item with a new code.
- **ItemType:** Always `RAW_MATERIAL`. The importer never creates `FINISHED_GOODS` records.

---

## 5. Bill of Materials (BOM)

**Applies to:** BOMs whose Finished SKU is a Raw Material item (e.g. assembled raw material kits).  
**Controlled by:** AaramBooks  
**Sub-Engine:** Raw Material Master Data Sub-Engine

- **Immutable Identity:** Content — defined as the combination of: Target SKU + Component SKUs + Quantities + Wastage %. The `BOM Number` in the import file is the business identifier for grouping rows.
- **Versioning:** Content-based. If exact content matches an existing active BOM for the same BOM Number → IGNORE. If content differs → create NEW VERSION and archive the previous active version. Never overwrite an existing active BOM.
- **Dependency Order:** BOM import requires that all referenced SKUs (target and component) already exist in the database. Missing SKU dependency → FAIL.
- **Constraints:** No `(bom_id, component_item_id)` unique constraint in the database. Exact duplicate component lines in the same import batch are deduplicated at the application layer.
- **Archived BOMs:** Exported with `--include-archived` flag. Not re-importable (ignored or mapped to current version).

---

# SKU Master Data Sub-Engine

**Controller:** ShopDeck Catalogue  
**Source of Truth:** ShopDeck Master Catalogue CSV  
**Status:** ⏳ FUTURE — Not yet implemented  
**CLI:** `python scripts/manage_imports.py --entity [FG_CATEGORY|SKU_CATALOGUE]` (future)

> [!IMPORTANT]
> **Finished Goods category import/export is NOT handled by the Raw Material Master Data Sub-Engine.**  
> All logic for FG taxonomy, FG SKU creation, and ShopDeck catalogue synchronization belongs exclusively in the SKU Master Data Sub-Engine.

---

## 6. Finished Goods Categories

**Applies to:** Root ancestor: `FG` and all its descendants.  
**Controlled by:** ShopDeck Catalogue synchronization  
**Sub-Engine:** SKU Master Data Sub-Engine *(future)*

> [!IMPORTANT]
> `CategoryModel.item_type` must never be used for domain classification. Hierarchy traversal is the sole authoritative source of truth.

- Finished Goods categories represent the ShopDeck product taxonomy, not AaramBooks-invented taxonomy.
- Manual creation of FG sub-categories outside of the ShopDeck catalogue synchronization is controlled — not freely allowed.
- Rules for this entity will be defined when the SKU Master Data Sub-Engine is implemented.

---

## 7. Finished Goods SKUs

**Applies to:** All `item_type = FINISHED_GOODS` records.  
**Controlled by:** ShopDeck Master Catalogue CSV  
**Sub-Engine:** SKU Master Data Sub-Engine *(future)*

- FG SKU creation and updates are driven by ShopDeck catalogue exports.
- The identity model, barcode rules, and attribute governance for FG SKUs will be defined in the SKU sub-engine.
- Rules for this entity will be defined when the SKU Master Data Sub-Engine is implemented.

---

*Last updated: 2026-08-18 — Split Category rules by sub-engine domain ownership.*
