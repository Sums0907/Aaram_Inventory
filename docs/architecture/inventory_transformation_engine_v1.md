# Inventory Transformation Engine Specification v1.0

## 0. Design Principles
The Inventory Transformation Engine is designed around the following principles:
- Inventory Truth is immutable.
- Every transformation must be mathematically traceable.
- No inventory update may occur without an immutable movement.
- Business workflows trigger transformations; they do not perform inventory calculations.
- The Transformation Engine is inventory-type agnostic.
- The engine must remain reusable for future manufacturing, repacking, assembly and disassembly workflows.
- **The Inventory Transformation Engine does not update inventory directly. It converts business events into mathematically valid, immutable inventory movements. The Inventory Truth Engine remains the sole authority responsible for calculating inventory balances. This separation ensures complete traceability, deterministic calculations, and future extensibility across all inventory transformation workflows.**

## 1. Responsibilities
The Transformation Engine is responsible for:
- Calculating component consumption.
- Validating BOM.
- Updating Job Worker pending inventory logic by emitting movements.
- Emitting immutable inventory movements.
- Recording the transformation.
- Returning the inventory impact summary.

The engine is **not** responsible for:
- Creating Goods Receipts.
- Managing Purchase Orders.
- Managing Vendors.
- Scheduling manufacturing.
- User interface logic.

## 2. Engine Contract

### Input
```text
Transformation Request
Transformation Reason
Reference Document
Source Inventory Items
Destination Inventory Items
Job Worker (optional)
Transformation Date
```

### Output
```text
Inventory Movements
Inventory Balance Updates (via Truth Engine)
Transformation Record
Updated Job Worker Inventory
Validation Result
```

## 3. Core Concepts
- **Inventory Item**: The generic building block. A Transformation Engine does not care if an item is a Bedsheet or Raw Cotton; it only sees Source and Destination inventory items.
- **Bill of Materials (BOM)**: Each BOM consists of:
  - Parent Inventory Item
  - Component Inventory Item
  - Required Quantity
  - Unit of Measure
  - Effective From Date
  - Effective To Date (future)
  - Active Status

## 4. Mathematical Formula
Total Component Consumption = Produced Quantity × BOM Quantity Per Unit

**Example:**
```text
100 Bedsheets
×
2.8 metres
=
280 metres Fabric
```

## 5. Transformation Lifecycle
```text
Business Document
↓
Transformation Request
↓
Inventory Transformation Engine
↓
Inventory Truth Engine
↓
Inventory Ledger
↓
Inventory Balances
```

## 6. Inventory Impact
A successful transformation always results in:
```text
Source Inventory
↓
Decrease

Destination Inventory
↓
Increase

Job Worker Pending Inventory
↓
Decrease

Transformation Register
↓
Insert Record

Inventory Ledger
↓
Insert Movements
```

## 7. Validation Rules
The engine shall reject a Transformation Request if:
- Destination Item has no active BOM.
- Component Inventory Item does not exist.
- Component Unit of Measure is incompatible.
- Required component quantity exceeds pending Job Worker inventory.
- Reference Document is missing.
- Transformation quantity is zero or negative.

## 8. Movement Types
The engine strictly relies on the following immutable movement types:
- `JOB_WORK_ISSUE`: Decreases main stock, increases Job Worker pending stock.
- `JOB_WORK_RECEIPT`: Increases main stock of finished goods.
- `JOB_WORK_RETURN`: Returns unused raw material from the Job Worker back to the main warehouse.
- `RAW_MATERIAL_CONSUMPTION`: Permanently deducts raw material from the Job Worker pending stock due to transformation.
- `INVENTORY_TRANSFORMATION`: A traceability movement linking the consumption to the receipt.

## 9. Goods Receipt Types
Generic Purchase Receipts are now split into distinct workflows:
- `RAW_MATERIAL_RECEIPT`: Procuring new raw materials.
- `PURCHASED_FINISHED_GOODS`: Procuring pre-made goods (no transformation).
- `JOB_WORK_RECEIPT`: Receiving goods created from company-owned raw materials (triggers Transformation Engine).

## 10. Transformation Reasons
- `JOB_WORK` (Initial Scope)
- `MANUFACTURING`
- `REPACKING`
- `KIT_ASSEMBLY`
- `DISASSEMBLY`
- `OTHER`

## 11. Transformation Register
The `InventoryTransformationRecord` acts as the definitive manufacturing journal, storing:
```text
Transformation ID
Transformation Date
Transformation Reason
Reference Type
Reference Number
Job Worker
Source Item
Destination Item
Source Quantity
Destination Quantity
Created By
Created At
```

## 12. Future Workflows
The engine shall support:
- Job Work
- In-house Manufacturing
- Repacking
- Bundle Creation
- Kit Assembly
- Product Disassembly
- Product Conversion
without requiring architectural changes.
