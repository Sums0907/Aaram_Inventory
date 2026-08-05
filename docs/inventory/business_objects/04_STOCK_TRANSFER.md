# Stock Transfer

## Purpose

The Stock Transfer Business Object represents the controlled movement of inventory between warehouses within the same organization.

A Stock Transfer ensures inventory is relocated while maintaining complete traceability and auditability.

A Stock Transfer never changes the organization's total inventory.

It only changes the warehouse in which the inventory is stored.

---

# Responsibilities

Stock Transfer is responsible for:

* Moving inventory between warehouses.
* Maintaining complete transfer history.
* Tracking inventory while in transit.
* Recording transfer approvals.
* Supporting multi-warehouse inventory operations.
* Providing complete audit trails.

Stock Transfer is **not** responsible for:

* Purchasing inventory.
* Selling inventory.
* Adjusting inventory quantities.
* Calculating inventory balances.
* Managing customer orders.

---

# Business Attributes

## Identification

| Attribute       | Description                |
| --------------- | -------------------------- |
| Transfer Number | Unique business identifier |
| Transfer Date   | Date transfer initiated    |
| Status          | Current lifecycle status   |

---

## Source Warehouse

| Attribute      | Description                 |
| -------------- | --------------------------- |
| From Warehouse | Warehouse sending inventory |

---

## Destination Warehouse

| Attribute    | Description                   |
| ------------ | ----------------------------- |
| To Warehouse | Warehouse receiving inventory |

---

## Transfer Items

Each transfer may contain multiple SKUs.

For every line:

| Attribute       | Description          |
| --------------- | -------------------- |
| SKU             | Inventory SKU        |
| Quantity        | Quantity transferred |
| Unit of Measure | Inventory Unit       |

---

## Audit Information

| Attribute    | Description |
| ------------ | ----------- |
| Requested By | User        |
| Approved By  | User        |
| Received By  | User        |
| Created On   | Timestamp   |
| Updated On   | Timestamp   |

---

# Validation Rules

* Transfer Number must be unique.
* Source Warehouse is mandatory.
* Destination Warehouse is mandatory.
* Source and Destination Warehouses must be different.
* At least one Transfer Item is required.
* Every Transfer Item must reference one SKU.
* Quantity must be greater than zero.
* Status is mandatory.

---

# Business Rules

## Rule 1

A Stock Transfer does not change total inventory.

---

## Rule 2

Every transfer generates two Inventory Movements.

```text id="7obm5k"
TRANSFER_OUT

↓

Source Warehouse

TRANSFER_IN

↓

Destination Warehouse
```

---

## Rule 3

Transfer quantities must always match.

Example:

```text id="6ovt8y"
Warehouse A

20 Units Out

↓

Warehouse B

20 Units In
```

---

## Rule 4

Transfer Out and Transfer In belong to the same Transfer document.

---

## Rule 5

Inventory remains in transit until received.

Future versions may support explicit "In Transit" inventory.

---

## Rule 6

Cancelled transfers must not affect Inventory Balance.

---

## Rule 7

Completed transfers automatically create the corresponding Inventory Movements.

---

## Rule 8

A transfer may contain multiple SKUs.

Each SKU generates its own pair of Inventory Movements.

---

# Relationships

Stock Transfer relates to:

* Warehouse
* Inventory Movement
* SKU
* Inventory Balance

---

# Lifecycle

```text id="lmw9mw"
DRAFT

↓

PENDING_APPROVAL

↓

APPROVED

↓

IN_TRANSIT

↓

RECEIVED

↓

COMPLETED

or

CANCELLED
```

Only COMPLETED transfers affect inventory balances.

---

# Transfer Workflow

```text id="o0wypf"
Transfer Requested

↓

Approval

↓

Inventory Picked

↓

Transfer Out

↓

Goods In Transit

↓

Goods Received

↓

Transfer In

↓

Transfer Completed
```

---

# Inventory Impact

Example

Warehouse A

```text id="d2ib7u"
Before

100 Units

↓

Transfer Out

20 Units

↓

After

80 Units
```

Warehouse B

```text id="3o1qxy"
Before

40 Units

↓

Transfer In

20 Units

↓

After

60 Units
```

Organization Total

```text id="7nd8b0"
Before

140 Units

↓

After

140 Units
```

---

# Reporting Impact

Stock Transfers contribute to:

* Warehouse Transfer Report
* Transfer History
* In Transit Inventory Report
* Warehouse Movement Report
* Inventory Ledger

---

# Examples

## Example

Transfer Number

TR-000025

Source Warehouse

Delhi Warehouse

Destination Warehouse

Jaipur Warehouse

Items

| SKU           | Quantity |
| ------------- | -------: |
| BEDSHEET-001  |       20 |
| COMFORTER-005 |       10 |

Inventory Result

* Delhi Warehouse decreases by 20 and 10 units respectively.
* Jaipur Warehouse increases by 20 and 10 units respectively.
* Total organization inventory remains unchanged.

---

# Future Enhancements

Future versions may support:

* Multi-stage transfers
* Transit warehouses
* Barcode-based transfers
* Batch/Lot transfers
* Serial number transfers
* Transfer scheduling
* Vehicle tracking
* Transfer costing

---

# Guiding Principle

**A Stock Transfer relocates inventory without changing total inventory.**

Every completed transfer must produce equal and opposite Inventory Movements, ensuring that inventory remains fully traceable while preserving the organization's total stock.
