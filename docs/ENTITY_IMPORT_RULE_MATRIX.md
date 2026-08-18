# Entity Import Rule Matrix

This document defines the strict governance rules for the Master Data Importer.

## General Rules
- **EXACT MATCH:** Ignore record (No action).
- **PARTIAL MATCH:** Apply entity-specific update rules.
- **NO MATCH:** Create new record.
- **AMBIGUOUS MATCH:** Reject row (Manual review required).
- **NO SILENT MERGES:** Never silently merge uncertain records.

## 1. Supplier
- **Immutable Identity:** Internal Supplier ID (if provided).
- **Mutable Fields:** GSTIN, Name, Phone Number, Email, Address, Remarks.
- **Protected Fields:** Is Job Worker (requires operational validation).
- **Matching Priority:** 1. ID. 2. GSTIN/Name/Phone (Controlled secondary matching).
- **Constraints:** Phone number and GSTIN are NOT unique constraints in the database. Ambiguous matches (e.g., matching phone but completely different name/GSTIN) must be rejected.

## 2. Unit of Measure (UOM)
- **Immutable Identity:** UOM Code.
- **Mutable Fields:** UOM Name, Short Name, Description, Status.
- **Protected Fields:** Type (INTEGER vs DECIMAL).
- **Matching Priority:** 1. UOM Code.

## 3. Category
- **Immutable Identity:** Category Code.
- **Mutable Fields:** Category Name, Description, Status.
- **Protected Fields:** Parent Category Code.
- **Root Protection:** The 5 root categories (Finished Goods, Raw Materials, Packaging, Consumables, Assets) are IMMUTABLE. They cannot be renamed, deleted, archived, or reparented.
- **Finished Goods vs Operational:** Finished Goods categories are governed by the Master Catalogue. Operational categories (Raw Materials, etc.) allow manual creation and import updates.
- **Ownership:** 1 SKU = 1 Category. Attributes belong to SKUs, not Categories.

## 4. Product & SKU
- **Immutable Identity:** SKU Code, Item Code, Barcode, Product Code.
- **Mutable Fields:** Size, Color, Attributes, Pricing, Packaging, Image URLs, Status.
- **Protected Fields:** Category ID, UOM ID.
- **Rules:** Never allow changing identity codes. To correct a code, create a new SKU.

## 5. Bill of Materials (BOM)
- **Immutable Identity:** Content (Target SKU, Component SKUs, Quantities, UOM, Wastage %, Tolerance %).
- **Versioning:** Content-based. If exact content matches an active BOM, IGNORE (do not create new version). If content differs, create NEW VERSION. Never overwrite an existing active BOM.
- **Constraints:** NO `(bom_id, component_item_id)` unique constraint in the DB. Repeated lines are allowed if business rules permit, but exact duplicate lines in the same import row are ignored/rejected based on validation.
