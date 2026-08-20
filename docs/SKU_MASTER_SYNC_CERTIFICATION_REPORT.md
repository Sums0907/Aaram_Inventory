# SKU Master Sync Certification Report

## 1. Code Audit Findings (Phase 8.1)

### Identity Verification
- `shopdeck_sku_id` in `SKUModel` is strictly used as the external matching identity.
- Evaluated `sku_matcher.py`: Identity matching strictly queries `shopdeck_sku_id`. Internal IDs, `item_code` and `sku_code` are generated entirely isolated from the sync matching engine and are never used to overwrite or incorrectly resolve a ShopDeck entity.

### Quantity Isolation
- **Rule SKU-SYNC-RULE-001 Confirmed**: The `ShopDeckReader` (`shopdeck_reader.py`) explicitly drops the `Quantity` field during row normalization immediately after parsing. It is never included in the parsed dictionaries passed to the validation, matching, diff or commit engines.
- **Inventory Separation**: A search through the `src/domains/sku_master_sync` module reveals zero imports or updates touching `inventory_movements`, `inventory_ledgers`, `warehouse_stock` or `InventoryBalanceModel`.

### Database Boundary Audit
- The commit engine transactions (`sku_creator.py`, `sku_updater.py`, `sku_archiver.py`, `sku_sync_service.py`) interact exclusively with the allowed domains:
  - `ProductModel`
  - `SKUModel`
  - `PricingModel`
  - `PackagingModel`
  - `ImportAuditLogModel`
- No forbidden stock modules are updated. Category ownership correctly delegates through `CategoryOwnershipResolver` without mutating unrelated tables.

## 2. Certification Results (Phase 8.2)

| Rule ID | Name | Result | Evidence / DB Verification |
|---|---|---|---|
| **SKU-001** | Existing SKU unchanged | PASSED | `test_sku_001_and_002_and_003_updates_and_ignores`: Exact match results in `IGNORED` diff, no writes. |
| **SKU-002** | Existing SKU attribute update | PASSED | `test_sku_001_and_002...`: Field diff recognized, `UPDATED` processed correctly. |
| **SKU-003** | Product Code change | PASSED | `test_sku_001_and_002...`: Target Product Code correctly mutated without Identity impact. |
| **SKU-004** | New SKU creation | PASSED | `test_sku_004_new_sku_creation`: Missing Identity processed as `CREATED`, cascading row inserts (Product, SKU, Pricing) completed transactionally. |
| **SKU-005** | Quantity ignored | PASSED | `test_sku_005_and_009_inventory_isolation`: High quantity injection dropped entirely. Resulted in NO CHANGE. |
| **SKU-006** | Missing SKU archive | PASSED | `test_sku_006_and_011_archive_and_reactivation`: Omitted active SKU set to `INACTIVE`. |
| **SKU-007** | Finished Goods category | PASSED | `FinishedGoodsCategorySync.resolve` correctly intercepts paths, verifies against `DomainType.FINISHED_GOODS`. |
| **SKU-008** | Duplicate Sku Id detection | PASSED | `test_sku_008_duplicate_sku_id_detection`: Batch execution halted and marked `FAILED` cleanly. |
| **SKU-009** | Inventory isolation | PASSED | DB `InventoryMovementModel` / balances checked post-sync, counts remained at 0. |
| **SKU-010** | Product Code collision | PASSED | `test_sku_010_product_code_collision`: Attempted takeover of active product codes blocks sync, flagged as Validation Error. |
| **SKU-011** | Archived SKU reactivation | PASSED | `test_sku_006_and_011...`: Resurfaced ID restored `ACTIVE` status instead of throwing errors. |
| **SKU-012** | Snapshot idempotency | PASSED | `test_sku_012_idempotency`: Re-running exact CSV outputted `0` mutations, cleanly marked `IGNORED`. |

## 3. Real ShopDeck Catalogue Dry-Run (Phase 8.3 / Phase 8.4)

Test ran against actual data (`input/sku_catalogues.csv`).

**Report Excerpt:**
```text
Created: 67
Updated: 0
Archived: 0
Ignored: 0
Failed: 0
```
- **Quantity Column Detected & Ignored:** The column `Quantity` existed in the `sku_catalogues.csv` with varying counts (e.g., `1`), but was dropped instantly. Zero updates targeted inventory.
- **Validation Errors:** None. All rows successfully resolved correctly as `CREATED`.

## 4. Migration Safety Review (Phase 8.5)

- **Preservation:** Migration `4118e8621401` added column `shopdeck_sku_id` as `VARCHAR(100)` and `NULLABLE=True`. Existing SKU objects were untouched.
- **Constraints:** Uniqueness rules were preserved. Since it defaults to NULL on existing records, data isn't corrupted.

## 5. Final Recommendation
The SKU Master Sync Engine has been successfully certified against all frozen business rules and architectural invariants. No forbidden tables are touched, the quantity boundary is respected, and idempotency is strictly handled.

**Recommendation: The engine is production-safe.**
