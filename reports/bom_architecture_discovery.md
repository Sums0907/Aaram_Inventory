# Phase 0 Architecture Discovery

## 1. What is already implemented
- `GoodsReceiptService.create()` supports the `GoodsReceiptType.JOB_WORK_RECEIPT` workflow.
- `InventoryTransformationEngine` exists with `validate_transformation` and `execute_transformation` logic.
- `BOMModel` and `BOMItemModel` are implemented with a schema capable of handling decimals (`Numeric(10, 4)`).
- `JobWorkerInventoryModel` tracks pending raw material stocks.

## 2. What is actually connected
The execution chain is connected exactly as requested:
`JOB_WORK_RECEIPT` -> `BOM lookup` (inside `TransformationEngine`) -> `BOM validation` -> `Consumption calculation` -> `RAW_MATERIAL_CONSUMPTION` movement -> `JOB_WORK_RECEIPT` movement -> `INVENTORY_TRANSFORMATION` record -> `Job Worker Pending Stock update`.

## 3. What is missing
- **Atomicity**: The transaction boundaries are disconnected. `GoodsReceiptService` flushes the GRN to the database and calls `InventoryMovementService`, and *then* invokes `TransformationEngine.execute_transformation`. The `execute_transformation` logic spins up its own internal `session` context manager. If a partial failure happens midway through iterating BOM components (e.g., insufficient stock on the 3rd component), the receipt and earlier consumption movements are orphaned, violating Phase 13 (Atomicity).
- **Duplicate BOM Prevention**: The current `BOMService` does not validate whether duplicate identical component lines are submitted within a single BOM.

## 4. What is currently different from the BOM specification
- **CRITICAL MATHEMATICAL DISCREPANCY**: The `InventoryTransformationEngine` currently uses `float()` and `int()` casting for consumption mathematics instead of Python's `Decimal` type.
  - Specifically, it calculates `required_qty = float(bom_item.quantity) * request.target_quantity`.
  - It then truncates this directly to an integer when updating job worker stock: `jw_stock.consumed_quantity += int(required_qty)` and when generating inventory movements: `quantity=-int(required_qty)`. 
  - This means a component requiring `2.875m * 100` (`287.5m`) will be forced into an integer `-287`, completely corrupting the Inventory Truth for decimals. Tests Phase 4 and Phase 14 are guaranteed to fail as currently implemented.

This report establishes the baseline prior to writing the `scripts/certify_bom_module.py` test suite.
