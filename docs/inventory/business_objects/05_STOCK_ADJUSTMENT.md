# Stock Adjustment

## Purpose

The Stock Adjustment Business Object records manual corrections to inventory when the physical stock differs from the system stock.

Inventory discrepancies may arise due to damaged goods, theft, counting errors, excess inventory, manufacturing losses, or operational mistakes.

Every correction must be recorded as a Stock Adjustment and must generate one or more Inventory Movements.

Inventory quantities must never be edited directly.

---

# Responsibilities

Stock Adjustment is responsible for:

* Correcting inventory discrepancies.
* Recording inventory gains and losses.
* Maintaining complete adjustment history.
* Supporting physical stock verification.
* Maintaining complete audit trails.
* Creating Inventory Movements for every adjustment.

Stock Adjustment is **not** responsible for:

* Recording normal sales.
* Recording purchases.
* Managing reservations.
* Managing warehouse transfers.
* Calculating inventory balances.

---

# Business Attributes

## Identification

| Attribute         | Description                |
| ----------------- | -------------------------- |
| Adjustment Number | Unique business identifier |
| Adjustment Date   | Date of adjustment         |
| Status            | Current lifecycle status   |

---

## Warehouse Information

| Attribute | Description              |
| --------- | ------------------------ |
| Warehouse | Warehouse being adjusted |

---

## Adjustment Items

Each adjustment may contain multiple SKUs.

For every line:

| Attribute           | Description                                     |
| ------------------- | ----------------------------------------------- |
| SKU                 | Inventory SKU                                   |
| System Quantity     | Quantity before adjustment                      |
| Physical Quantity   | Actual counted quantity                         |
| Adjustment Quantity | Difference between system and physical quantity |
| Unit of Measure     | Inventory Unit                                  |

---

## Adjustment Information

| Attribute       | Description                    |
| --------------- | ------------------------------ |
| Adjustment Type | Stock Gain or Stock Loss       |
| Reason          | Business reason for adjustment |
| Remarks         | Additional notes               |

---

## Audit Information

| Attribute    | Description |
| ------------ | ----------- |
| Requested By | User        |
| Approved By  | User        |
| Created On   | Timestamp   |
| Updated On   | Timestamp   |

---

# Adjustment Types

The Inventory Engine supports the following adjustment types.

| Adjustment Type      | Inventory Effect     |
| -------------------- | -------------------- |
| STOCK_GAIN           | Increase             |
| STOCK_LOSS           | Decrease             |
| DAMAGED_GOODS        | Decrease             |
| LOST_INVENTORY       | Decrease             |
| FOUND_INVENTORY      | Increase             |
| PHYSICAL_STOCK_COUNT | Increase or Decrease |
| MANUAL_CORRECTION    | Increase or Decrease |

Additional adjustment types may be introduced in future versions.

---

# Validation Rules

* Adjustment Number must be unique.
* Warehouse is mandatory.
* At least one Adjustment Item is required.
* SKU is mandatory.
* Physical Quantity cannot be negative.
* Reason is mandatory.
* Status is mandatory.

---

# Business Rules

## Rule 1

Inventory quantities must never be edited directly.

Every correction must generate an Inventory Movement.

---

## Rule 2

Each Adjustment Item creates exactly one Inventory Movement.

---

## Rule 3

The Adjustment Quantity is calculated.

```text id="8zfrq0"
Adjustment Quantity

=

Physical Quantity

-

System Quantity
```

Users cannot manually enter the adjustment quantity.

---

## Rule 4

Positive Adjustment Quantities generate inventory increases.

Negative Adjustment Quantities generate inventory decreases.

---

## Rule 5

Completed adjustments immediately update Inventory Balance through Inventory Movements.

---

## Rule 6

Cancelled adjustments do not affect inventory.

---

## Rule 7

Every adjustment requires a reason.

Reason is mandatory for audit purposes.

---

## Rule 8

Physical stock counts may produce both stock gains and stock losses within the same adjustment document.

---

## Rule 9

Stock Adjustments are immutable after completion.

Corrections must be performed through a new adjustment.

---

# Relationships

Stock Adjustment relates to:

* Warehouse
* SKU
* Inventory Movement
* Inventory Balance

---

# Lifecycle

```text id="a2m1s5"
DRAFT

↓

PENDING_APPROVAL

↓

APPROVED

↓

COMPLETED

or

CANCELLED
```

Only COMPLETED adjustments affect inventory balances.

---

# Adjustment Workflow

```text id="30glwu"
Physical Stock Count

↓

Difference Identified

↓

Create Adjustment

↓

Approval

↓

Inventory Movement Created

↓

Inventory Balance Updated
```

---

# Inventory Impact

Example

System Stock

100 Units

Physical Count

95 Units

```text id="i0myak"
Adjustment Quantity

95

-

100

=

-5 Units
```

Inventory Result

* Inventory decreases by 5 units.
* Inventory Movement of type STOCK_LOSS is created.

---

# Reporting Impact

Stock Adjustments contribute to:

* Stock Adjustment Report
* Inventory Ledger
* Physical Stock Verification Report
* Inventory Valuation Report
* Warehouse Inventory Report
* Audit Report

---

# Examples

## Example 1 – Damaged Goods

Adjustment Number

ADJ-000021

Warehouse

Delhi Warehouse

SKU

BEDSHEET-001

System Quantity

50

Physical Quantity

48

Reason

Damaged During Storage

Inventory Result

2 Units Removed

---

## Example 2 – Physical Stock Count

Warehouse

Jaipur Warehouse

SKU

COMFORTER-005

System Quantity

120

Physical Quantity

123

Reason

Physical Verification

Inventory Result

3 Units Added

---

# Future Enhancements

Future versions may support:

* Cycle Count Programs
* Barcode-based Stock Counts
* Mobile Inventory Verification
* Batch/Lot Adjustments
* Serial Number Adjustments
* Approval Workflows by Value
* AI-assisted Variance Detection

---

# Guiding Principle

**Inventory corrections must never bypass the Inventory Engine.**

Every discrepancy between physical stock and system stock must be resolved through a Stock Adjustment, ensuring that every inventory change remains fully traceable, auditable, and reproducible through immutable Inventory Movements.
