# Inventory Movement

## Purpose

The Inventory Movement Business Object is the foundation of the Inventory Engine.

Every change to inventory—whether caused by a sale, purchase, transfer, return, reservation, or adjustment—must be represented as an Inventory Movement.

The Inventory Movement is the single source of truth for inventory history.

Inventory quantities are never edited directly. Instead, the Inventory Engine derives current stock positions from the complete history of Inventory Movements.

---

# Responsibilities

The Inventory Movement is responsible for:

* Recording every inventory transaction.
* Maintaining a complete inventory audit trail.
* Tracking inventory changes at the SKU and Warehouse level.
* Providing the source data for Inventory Balance calculations.
* Linking inventory changes to the originating business document.
* Publishing inventory events for downstream domains.

The Inventory Movement is **not** responsible for:

* Calculating inventory balances.
* Reserving inventory.
* Matching business documents.
* Creating accounting entries.
* Updating warehouse master data.

---

# Business Attributes

## Identification

| Attribute       | Description                       |
| --------------- | --------------------------------- |
| Movement Number | Unique business identifier        |
| Movement Type   | Type of inventory transaction     |
| Movement Date   | Date and time of the movement     |
| Posting Date    | Accounting/Inventory posting date |
| Status          | Current lifecycle status          |

---

## Warehouse Information

| Attribute | Description                       |
| --------- | --------------------------------- |
| Warehouse | Warehouse where movement occurred |

---

## SKU Information

| Attribute       | Description                     |
| --------------- | ------------------------------- |
| SKU             | Inventory SKU                   |
| Unit of Measure | Stock unit                      |
| Quantity        | Movement quantity               |
| Unit Cost       | Cost per unit (when applicable) |

---

## Reference Information

| Attribute        | Description                   |
| ---------------- | ----------------------------- |
| Reference Type   | Originating business document |
| Reference Number | Business document number      |
| Reference ID     | Internal UUID                 |

Examples of Reference Types:

* Opening Stock
* Sales Order
* Purchase Receipt
* Stock Adjustment
* Warehouse Transfer
* Manufacturing Order
* Customer Return
* Supplier Return

---

## Audit Information

| Attribute  | Description |
| ---------- | ----------- |
| Created By | User/System |
| Created On | Timestamp   |
| Updated By | User/System |
| Updated On | Timestamp   |

---

# Inventory Movement Types

The Inventory Engine supports the following movement types.

| Movement Type       | Inventory Effect     |
| ------------------- | -------------------- |
| OPENING_STOCK       | Increase             |
| PURCHASE            | Increase             |
| PURCHASE_RETURN     | Decrease             |
| SALE                | Decrease             |
| CUSTOMER_RETURN     | Increase             |
| SUPPLIER_RETURN     | Decrease             |
| TRANSFER_IN         | Increase             |
| TRANSFER_OUT        | Decrease             |
| STOCK_ADJUSTMENT    | Increase or Decrease |
| RESERVATION         | No Physical Change   |
| RESERVATION_RELEASE | No Physical Change   |
| MANUFACTURING_IN    | Increase             |
| MANUFACTURING_OUT   | Decrease             |

Additional movement types may be introduced without changing the overall architecture.

---

# Validation Rules

* Movement Number must be unique.
* Movement Type is mandatory.
* Movement Date is mandatory.
* Warehouse is mandatory.
* SKU is mandatory.
* Quantity cannot be zero.
* Quantity must always be positive. The movement type determines whether it is treated as inbound or outbound.
* Reference Type is mandatory.
* Reference Number is mandatory.
* Status is mandatory.

---

# Business Rules

## Rule 1

Every inventory change must originate from an Inventory Movement.

---

## Rule 2

Inventory Movements are immutable.

Posted movements cannot be edited.

---

## Rule 3

Inventory Movements cannot be deleted.

Corrections must always be recorded through new Inventory Movements.

---

## Rule 4

Only POSTED movements affect Inventory Balance.

Draft and Cancelled movements are ignored during balance calculations.

---

## Rule 5

Every Inventory Movement belongs to exactly one Warehouse.

---

## Rule 6

Every Inventory Movement belongs to exactly one SKU.

---

## Rule 7

Warehouse Transfers always create two Inventory Movements:

* Transfer Out
* Transfer In

---

## Rule 8

Reservations do not change physical inventory.

They only affect Available Quantity.

---

## Rule 9

Inventory Balance must never be manually updated from this Business Object.

Balances are always calculated from posted Inventory Movements.

---

## Rule 10

Every movement must reference the business document that created it.

Complete traceability is mandatory.

---

# Relationships

Inventory Movement has relationships with:

* Warehouse
* SKU
* Sales Order
* Purchase Receipt (Future)
* Stock Transfer
* Stock Adjustment
* Manufacturing Order (Future)

---

# Lifecycle

```text
DRAFT

↓

POSTED

↓

CANCELLED
```

Once POSTED, the movement becomes immutable.

Cancelled movements remain in history for audit purposes.

---

# Permissions

| Action          | Permission        |
| --------------- | ----------------- |
| Create Movement | Inventory Manager |
| Post Movement   | Inventory Manager |
| Cancel Movement | Inventory Manager |
| View Movement   | Authorized Users  |

Deletion is never permitted.

---

# Events

The Inventory Movement Business Object publishes:

* InventoryMovementCreated
* InventoryMovementPosted
* InventoryMovementCancelled

Future domains such as Accounting and Reporting subscribe to these events.

---

# Reporting Impact

Inventory Movements contribute to:

* Inventory Ledger
* Inventory Balance
* Warehouse Stock Report
* SKU Stock Report
* Inventory Valuation
* Movement History
* Stock Adjustment Report
* Transfer Report

---

# Examples

## Sale

| Field            | Value           |
| ---------------- | --------------- |
| Movement Type    | SALE            |
| Warehouse        | Delhi Warehouse |
| SKU              | BEDSHEET-001    |
| Quantity         | 2               |
| Reference Type   | Sales Order     |
| Reference Number | SO-000145       |

Inventory Effect: **Decrease by 2 units**

---

## Purchase

| Field            | Value            |
| ---------------- | ---------------- |
| Movement Type    | PURCHASE         |
| Warehouse        | Delhi Warehouse  |
| SKU              | BEDSHEET-001     |
| Quantity         | 100              |
| Reference Type   | Purchase Receipt |
| Reference Number | PR-000025        |

Inventory Effect: **Increase by 100 units**

---

## Warehouse Transfer

Transfer Out

| Field         | Value           |
| ------------- | --------------- |
| Movement Type | TRANSFER_OUT    |
| Warehouse     | Delhi Warehouse |
| SKU           | BEDSHEET-001    |
| Quantity      | 20              |

Transfer In

| Field         | Value            |
| ------------- | ---------------- |
| Movement Type | TRANSFER_IN      |
| Warehouse     | Jaipur Warehouse |
| SKU           | BEDSHEET-001     |
| Quantity      | 20               |

Net Inventory Effect: **No change** (only warehouse location changes).

---

# Future Enhancements

Future versions may support:

* Batch/Lot Tracking
* Serial Number Tracking
* Expiry Management
* Manufacturing Consumption
* Manufacturing Production
* Multi-company Inventory
* AI-based Inventory Optimization

---

# Guiding Principle

**Every inventory change must be represented by an Inventory Movement.**

Inventory Movement is the immutable event that drives every inventory calculation within AaramBooks. Inventory Balance, Reservations, Transfers, Valuation, and future Inventory Intelligence are all derived from these recorded movements.
