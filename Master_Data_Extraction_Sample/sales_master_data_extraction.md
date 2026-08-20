# MASTER DATA EXTRACTION REPORT

This is a read-only inspection of the current AaramBooks Master Data implementation.

## 1. Suppliers
* **A. Current entity/model name:** `Supplier`
* **B. Database table name:** `masters_suppliers`
* **C. Frontend dialog/form:** `SupplierDialog` located at `frontend/src/components/suppliers/SupplierDialog.tsx`
* **D. Backend schema:** `SupplierCreate` / `SupplierUpdate` located at `src/domains/masters/schemas/supplier.py`
* **E & F. Fields:**
  * `id`: System UUID (System generated, uneditable)
  * `name`: String(255), Required, max_length=255
  * `gstin`: String(15), Optional, max_length=15
  * `contact_number`: String(50), Optional, max_length=50
  * `email`: String(255), Optional, max_length=255
  * `address`: Text, Optional
  * `remarks`: Text, Optional
  * `is_job_worker`: Boolean, Required, Default=`False`
* **G. Existing unique constraints/indexes:** None currently exist in the SQLAlchemy model (`contact_number` does NOT have `unique=True` in the database schema).
* **H. Existing foreign-key relationships:** None.
* **I. Existing API schemas:** `SupplierCreate` (name, gstin, contact_number, email, address, remarks, is_job_worker).

## 2. Unit of Measure (UoM)
* **A. Current entity/model name:** `UnitOfMeasureModel`
* **B. Database table name:** `units_of_measure`
* **C. Frontend dialog/form:** Inline dialog inside `UnitsOfMeasurePage` located at `frontend/src/pages/inventory/UnitsOfMeasurePage.tsx`
* **D. Backend schema:** `UnitOfMeasureCreate` / `UnitOfMeasureUpdate` located at `src/domains/masters/schemas/unit_of_measure.py`
* **E & F. Fields:**
  * `unit_code`: String(50), Required, Uneditable after creation
  * `unit_name`: String(100), Required
  * `short_name`: String(20), Required
  * `description`: String(255), Optional
  * `unit_type`: Enum string (`"INTEGER"`, `"DECIMAL"`), Required, Default=`"INTEGER"`
  * `status`: GenericStatus Enum, Required, Default=`ACTIVE`
* **G. Existing unique constraints/indexes:** `unit_code` (Unique, Indexed), `unit_name` (Unique), `short_name` (Unique).
* **H. Existing foreign-key relationships:** None.
* **I. Existing API schemas:** `UnitOfMeasureCreate` and `UnitOfMeasureUpdate` (where `unit_code` is omitted to prevent editing).

## 3 & 4. Catalogue / Inventory Items & Raw Materials
* **Design approach:** Catalogue/Finished Goods and Raw Materials currently use a **shared inventory-item model** (`ProductModel` + `SKUModel`) connected via a one-to-many relationship, distinguished by an `item_type` discriminator in the product table.
* **A. Current entity/model name:** `ProductModel` & `SKUModel`
* **B. Database table name:** `products` & `skus`
* **C. Frontend dialog/form:** `InventoryItemFormDialog.tsx`, `SKUFormDialog.tsx`, `ProductWorkspaceDialog.tsx` located at `frontend/src/components/products/`
* **D. Backend schema:** `InventoryItemCreate` located at `src/domains/masters/schemas/inventory_item.py`
* **E & F. Fields (`ProductModel`):**
  * `product_code`: String(50), Required, Indexed, Unique
  * `product_name`: String(150), Required
  * `description`: String(1000), Optional
  * `brand`: String(100), Optional
  * `product_type`: String(100), Optional
  * `item_type`: Enum (`ItemType`), Required, Default=`FINISHED_GOODS`
  * `status`: Enum (`GenericStatus`), Required, Default=`ACTIVE`
  * `category_id`: UUID, Optional (FK to `categories`)
* **E & F. Fields (`SKUModel`):**
  * `item_code`: String(50), Required, Indexed, Unique
  * `sku_code`: String(50), Optional, Indexed, Unique
  * `product_id`: UUID, Required (FK to `products`)
  * `size`, `color`, `pattern`, `material`, `thread_count`: String, Optional
  * `uom_id`: UUID, Optional (FK to `units_of_measure`)
  * `attribute_values`: JSONB, Required, Default=`{}`
  * `barcode`: String(100), Optional, Unique
  * `status`: Enum (`GenericStatus`), Required, Default=`ACTIVE`
* **G. Existing unique constraints/indexes:** `product_code`, `item_code`, `sku_code`, `barcode` are uniquely constrained and indexed.
* **H. Existing foreign-key relationships:** `product_id` -> `products.id`, `category_id` -> `categories.id`, `uom_id` -> `units_of_measure.id`.

## 5. Bill of Materials (BOM)
* **A. Current entity/model name:** `BOMModel` (Header) & `BOMItemModel` (Lines)
* **B. Database table name:** `masters_boms` & `masters_bom_items`
* **C. Frontend dialog/form:** `BOMFormDialog` located at `frontend/src/components/products/BOMFormDialog.tsx`
* **D. Backend schema:** `BOMCreate`, `BOMItemCreate` located at `src/domains/masters/schemas/bom.py`
* **E & F. Fields (`BOMModel`):**
  * `bom_number`: String(255), Required, Indexed
  * `bom_name`: String(255), Optional
  * `target_item_id`: UUID, Required, Indexed (Finished Product Reference)
  * `target_quantity`: Integer, Required, Default=`1`
  * `status`: String(50), Required, Default=`"DRAFT"`
  * `version`: Integer, Required, Default=`1`
  * `effective_from`: Date, Optional
  * `effective_to`: Date, Optional
* **E & F. Fields (`BOMItemModel`):**
  * `bom_id`: UUID, Required, Indexed (FK to `masters_boms`)
  * `component_item_id`: UUID, Required, Indexed (Component Reference)
  * `quantity`: Numeric(10,4), Required
  * `uom_id`: UUID, Optional, Indexed (FK to `units_of_measure`)
  * `unit_of_measure`: String(50), Required, Default=`"-"`
  * `wastage_percentage`: Numeric(5,2), Required, Default=`0.0`
  * `tolerance_percentage`: Numeric(5,2), Required, Default=`0.0`
* **G. Existing unique constraints/indexes:** No unique database constraint prevents duplicate Finished SKU + Component SKU combinations (No UniqueConstraint on `(bom_id, component_item_id)`).
* **H. Existing foreign-key relationships:** `target_item_id` and `component_item_id` -> `skus.id`. `uom_id` -> `units_of_measure.id`.

---

# MASTER DATA IMPORT CONTRACT — SOURCE EXTRACTION

### Supplier
| Field | Current DB/API field | Type | Required | Unique Key? | Editable | Notes |
|---|---|---|---|---|---|---|
| Phone Number | `contact_number` | String | No | **Mismatch** | Yes | Currently NOT marked unique in DB. |
| Supplier Name | `name` | String | Yes | No | Yes | |
| GSTIN | `gstin` | String | No | No | Yes | |
| Email | `email` | String | No | No | Yes | |
| Address | `address` | Text | No | No | Yes | |
| Remarks | `remarks` | Text | No | No | Yes | |
| Is Job Worker | `is_job_worker` | Boolean | Yes | No | Yes | Default: False |

### Unit of Measure (UoM)
| Field | Current DB/API field | Type | Required | Unique Key? | Editable | Notes |
|---|---|---|---|---|---|---|
| UoM Code | `unit_code` | String | Yes | **Yes** | No | |
| UoM Name | `unit_name` | String | Yes | Yes (DB) | Yes | |
| Short Name | `short_name` | String | Yes | Yes (DB) | Yes | |
| Type | `unit_type` | Enum | Yes | No | Yes | `INTEGER` or `DECIMAL` |

### Catalogue / Finished Goods / Raw Materials (Shared Model)
| Field | Current DB/API field | Type | Required | Unique Key? | Editable | Notes |
|---|---|---|---|---|---|---|
| Finished SKU Key | `sku_code` | String | No | **Yes** | Yes | Located on `SKUModel`. |
| Raw Material Key | `item_code` | String | Yes | **Yes** | Yes | Located on `SKUModel`. Internal key. |
| Base Product Code| `product_code` | String | Yes | Yes (DB) | Yes | Located on `ProductModel`. |
| Product Name | `product_name` | String | Yes | No | Yes | |
| Item Type | `item_type` | Enum | Yes | No | Yes | Discriminator (`FINISHED_GOODS` vs `RAW_MATERIAL`) |
| UoM Reference | `uom_id` | UUID | No | No | Yes | Authoritative component UoM |
| Category | `category_id` | UUID | No | No | Yes | |

### Bill of Materials (BOM)
| Field | Current DB/API field | Type | Required | Unique Key? | Editable | Notes |
|---|---|---|---|---|---|---|
| Finished Prod Ref| `target_item_id` | UUID | Yes | **No DB Constraint** | Yes | FK to `skus.id` |
| Component Ref | `component_item_id`| UUID | Yes | **No DB Constraint** | Yes | FK to `skus.id` |
| Target Quantity | `target_quantity`| Integer | Yes | No | Yes | |
| Component Qty | `quantity` | Numeric | Yes | No | Yes | |
| Component UoM | `uom_id` | UUID | No | No | Yes | |
| Sequence/Order | *(Not present)* | N/A | N/A | N/A | N/A | Sequence/Order fields do not exist |
| Effective From | `effective_from` | Date | No | No | Yes | |
| Effective To | `effective_to` | Date | No | No | Yes | |
| Version | `version` | Integer | Yes | No | Yes | |
| Status | `status` | String | Yes | No | Yes | |

---

# OPEN ISSUES / AMBIGUITIES

1. **Supplier Unique Key Mismatch:** The frozen business rule dictates that `Phone Number` is the unique key, but `contact_number` is currently neither required nor uniquely constrained in the database schema (`masters_suppliers` table).
2. **BOM Duplicate Combinations:** There is currently no database constraint enforcing uniqueness on the combination of `(bom_id, component_item_id)`. Duplicate component entries for the same finished product are not structurally prevented.
3. **SKU vs Item Code Mapping:** For Catalogue (Finished Goods), the frozen key is `SKU ID`. The database contains both `sku_code` (optional, unique) and `item_code` (required, unique). For Raw Materials, the frozen key is `Raw Material ID / SKU ID`, which likely maps to `item_code` since `sku_code` is optional and typically used for Finished Goods.
4. **BOM Sequence Numbering:** No `sequence` or `order` fields currently exist in `BOMItemModel`.
5. **No Existing Normalization Rules Documented:** There are no explicit normalizations (e.g., whitespace stripping, casing for codes, or phone number formatting) visible in the core Pydantic schemas or SQLAlchemy models for these master records.
