# SKU Master Sync Implementation Plan

## 1. Confirm SKU Identity Architecture

### Current Analysis
Currently, the database model `SKUModel` defines `item_code` (internal AaramBooks identifier) and `sku_code` (internal stock keeping unit code).

If we map the `ShopDeck Sku Id` directly to `SKUModel.item_code`, we risk mixing external identities with internal identities. Because AaramBooks may integrate with future external channels (e.g., Amazon, Myntra, Flipkart, Shopify), external identities should remain strictly isolated from the internal SKU identity structure.

### Architectural Decision & Proposal
We will **NOT** overload `SKUModel.item_code` with the ShopDeck Sku Id.

Instead, we propose introducing a new explicit external identity field on `SKUModel`:
```python
shopdeck_sku_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
```
**Migration Impact:**
- A new database migration script will be required to add `shopdeck_sku_id` to the `skus` table.
- Internal AaramBooks processes will continue to rely on `item_code` / `id` for relational mapping.
- The `ShopDeck Sku Id` from the CSV will map exclusively to `shopdeck_sku_id`, which will act as the single immutable external identity during the sync matching phase.

---

## 2. Strengthen Quantity Isolation Rule

**SKU-SYNC-RULE-001:** "ShopDeck Quantity is catalogue display data only and is not inventory data."

### Enforcement Flow
The ShopDeck Quantity field must be completely removed at the initial CSV parsing stage. 
```
CSV Input  ->  Parser removes Quantity  ->  Remaining SKU payload processed
```
The Quantity field must never enter:
- The validation layer
- The diff engine
- The update engine
- The audit comparison or reporting logs

Quantity must never update inventory or SKU stock fields, participate in row comparison, or appear as an update reason.

---

## 3. Database Model Mapping

Based on the isolated external identity approach, below is the mapping of ShopDeck CSV columns to the `AaramBooks` database schema:

| ShopDeck CSV Field | AaramBooks DB Entity | AaramBooks DB Field | Data Type / Rules |
| :--- | :--- | :--- | :--- |
| **Sku Id** | `SKUModel` | `shopdeck_sku_id` | Primary Immutable External Identifier (`String(100)`) |
| **Product Code** | `ProductModel` | `product_code` | Mutable (updated per Sku Id) |
| **Name** | `ProductModel` | `product_name` | String (`String(150)`) |
| **Selling Price** | `PricingModel` | `selling_price` | Numeric (replaces existing pricing) |
| **MRP** | `PricingModel` | `mrp` | Numeric |
| **Cost Price** | `PricingModel` | `cost_price` | Numeric |
| **GST %** | `PricingModel` | `gst_percentage` | Numeric |
| **Packaging Length** | `PackagingModel` | `length` | Numeric |
| **Packaging Breadth** | `PackagingModel` | `breadth` | Numeric |
| **Packaging Height** | `PackagingModel` | `height` | Numeric |
| **Packaging Weight** | `PackagingModel` | `weight` | Numeric |
| **Category Path** | `CategoryModel` | `category_id` | Resolved to `ProductModel.category_id` (Domain: `FG`) |
| **Attributes** | `SKUModel` | `attribute_values` | JSON mapping of varied product characteristics |
| **Quantity** | **IGNORED** | **IGNORED** | Stripped by parser per `SKU-SYNC-RULE-001` |

---

## 4. Implementation Boundaries

### Module Ownership

**Allowed Tables:**
- SKU master (`skus`)
- Product master (`products`)
- Pricing (`master_pricing`)
- Packaging (`master_packaging`)
- Finished Goods Category mapping (`categories`)
- Import audit logs (`import_audit_logs`)

**Forbidden Tables:**
- Inventory ledger (`inventory_ledgers`)
- Inventory movements (`inventory_movements`)
- Stock balances
- Warehouse quantity tables

---

## 5. Synchronisation Pipeline

The synchronisation follows an explicit round-trip and diffing pipeline:

1. **CSV Reader (`shopdeck_reader.py`)**
   - Parses the CSV input. Drops the `Quantity` field immediately per `SKU-SYNC-RULE-001`.
2. **Validator (`sku_validator.py`)**
   - Ensures essential identifiers exist (Sku Id) and rejects invalid formats.
3. **Category Resolver (`finished_goods_category_sync.py`)**
   - Asserts that all supplied categories belong to the `FG` (Finished Goods) domain.
4. **Identity Matching (`sku_matcher.py`)**
   - Matches incoming **Sku Id** against existing `SKUModel.shopdeck_sku_id`.
   - Groups records into **New SKUs**, **Existing SKUs**, and **Missing SKUs**.
5. **Diff Engine & Dry Run**
   - Compares mutable attributes to detect updates.
   - Calculates total CREATED, UPDATED, ARCHIVED rows.
6. **Commit Engine (`sku_creator.py` / `sku_updater.py` / `sku_archiver.py`)**
   - Applies all transformations and inserts/updates to the database upon commit.

---

## 6. Sku Id and Product Code Collision Protections

### Duplicate Sku Id Protection
Duplicate Sku Id rows within the same CSV payload are strictly forbidden. 
Two records cannot modify the same SKU identity in a single synchronisation batch.

- **Error Behaviour:** Reject duplicate identity rows explicitly.
- **Dry-run Reporting:** The duplication failure will be reported as a validation failure.
- **Commit Blocking:** If duplicates are detected, the batch synchronization for those specific identities fails, guaranteeing atomic safety.

### Product Code Collision Detection
While Product Code is mutable and updated based on ShopDeck Sku Id, two different Sku Ids cannot silently share the same Product Code if the database/business rules prohibit duplicate Product Codes.

- **Scenario:** Two different `ShopDeck Sku Id` map to the same `Product Code` within the CSV or against existing DB records.
- **Error Behaviour:** Reject conflicting rows explicitly.
- **Dry-run Reporting:** Mark as a validation failure and include a clear reason in the dry-run report.
- **Commit Blocking:** Prevent commit for those conflicting rows.

---

## 7. Missing SKU Handling & Archived SKU Reactivation

Missing SKUs are handled through an **Archive / Inactivate** policy.

- If an `ItemType.FINISHED_GOODS` SKU mapped to a `shopdeck_sku_id` exists in the DB but is absent from the CSV snapshot, it is marked as `GenericStatus.INACTIVE`.
- **Never Delete:** Because SKUs might have historical Inventory Movements, Accounting References, or Sales Orders, they are never purged from the `skus` table.

### Archived SKU Reactivation
- **Scenario:** An SKU disappears from the ShopDeck snapshot and is marked `INACTIVE`. In a future snapshot, the same `shopdeck_sku_id` appears again.
- **Expected Action:** `INACTIVE` → `ACTIVE`. DO NOT create a new SKU.
- **Preserved State:** The internal SKU id, historical references, inventory relationships, and `shopdeck_sku_id` remain identical. The immutable identity remains `shopdeck_sku_id`.

---

## 8. Audit and Reporting Design

### Metadata Extensions
Every `SHOPDECK_SKU_CATALOGUE_SYNC` batch should capture extended metadata to allow reconstruction of the ShopDeck snapshot that created the DB state:
- `source_system` = `SHOPDECK`
- `source_file_name`
- `source_file_hash`
- `catalogue_snapshot_date`
- `batch_id`
- `executing_user`
- `run_mode` = `DRY_RUN` / `COMMITTED`

### Dry Run Report Format
The expected dry-run output should clearly separate catalogue updates, ignored fields (like Quantity), and validation failures. Example:

```text
SHOPDECK SKU CATALOGUE SYNC REPORT

Created:
5

Updated:
32

Archived:
4

Ignored:
20

Failed:
1

Example row:

SKU ID:
12345

Changes:
Name:
Old Bedsheet
→
Premium Bedsheet

Selling Price:
1499
→
1599

Quantity:
500

Result:
IGNORED
Reason:
ShopDeck Quantity is not inventory data
```

---

## 9. Certification Test Plan

The final certification flow will cover the following scenarios:

- **SKU-001** Existing SKU unchanged → `IGNORE`
- **SKU-002** Existing SKU attribute change → `UPDATE`
- **SKU-003** Product Code change → `UPDATE`
- **SKU-004** New SKU creation → `CREATE`
- **SKU-005** Quantity ignored → `VERIFY NO INVENTORY IMPACT`
- **SKU-006** Missing SKU archive → `INACTIVE`
- **SKU-007** Finished Goods category validation
- **SKU-008** Duplicate Sku Id detection
- **SKU-009** Inventory isolation verification
- **SKU-010** Product Code collision detection
- **SKU-011** Archived SKU reactivation

### SKU-012 — ShopDeck Snapshot Idempotency

**Purpose:**
Verify that running the exact same ShopDeck catalogue snapshot multiple times does not create duplicate changes or mutate the database repeatedly. The SKU Master Sync Engine must be idempotent.

**Scenario:**
- **Initial execution:** Applies creations, updates, and archives from `ShopDeck CSV Snapshot A` against the database.
- **Second execution:** Re-running the exact same `ShopDeck CSV Snapshot A` yields:
  - Created: 0
  - Updated: 0
  - Archived: 0
  - Failed: 0
  - Ambiguous: 0
  - Ignored: All unchanged records
- **Verification Requirements:** 
  1. No duplicate SKU records created.
  2. No duplicate Product records created.
  3. No duplicate Pricing records created.
  4. No duplicate Packaging records created.
  5. No inventory tables changed.
  6. No unnecessary audit changes except a new synchronization audit record.
