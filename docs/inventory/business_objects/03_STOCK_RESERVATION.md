# Stock Reservation

## Purpose

The Stock Reservation Business Object represents inventory that has been temporarily allocated to one or more Sales Orders but has not yet left the warehouse.

A reservation reduces the Available Quantity without reducing the physical Quantity On Hand.

This enables the Inventory Engine to prevent overselling while maintaining an accurate representation of warehouse inventory.

Stock Reservations are temporary business objects.

They exist only until inventory is dispatched, released, or cancelled.

---

# Responsibilities

Stock Reservation is responsible for:

* Reserving inventory for customer orders.
* Preventing overselling.
* Managing reserved inventory.
* Releasing inventory when orders are cancelled.
* Supporting warehouse allocation.
* Tracking reservation history.

Stock Reservation is **not** responsible for:

* Updating physical inventory.
* Recording inventory movements.
* Dispatching inventory.
* Calculating inventory balances.
* Creating accounting entries.

---

# Business Attributes

## Identification

| Attribute          | Description                   |
| ------------------ | ----------------------------- |
| Reservation Number | Unique reservation identifier |
| Reservation Date   | Date reservation was created  |
| Status             | Reservation lifecycle         |

---

## Order Information

| Attribute   | Description         |
| ----------- | ------------------- |
| Sales Order | Related Sales Order |
| Customer    | Customer Name       |
| Order Date  | Sales Order Date    |

---

## Inventory Information

| Attribute         | Description       |
| ----------------- | ----------------- |
| Warehouse         | Warehouse         |
| SKU               | Reserved SKU      |
| Reserved Quantity | Quantity reserved |

---

## Audit Information

| Attribute   | Description |
| ----------- | ----------- |
| Created By  | User/System |
| Created On  | Timestamp   |
| Released By | User/System |
| Released On | Timestamp   |

---

# Validation Rules

* Reservation Number must be unique.
* Sales Order is mandatory.
* Warehouse is mandatory.
* SKU is mandatory.
* Reserved Quantity must be greater than zero.
* Reservation Status is mandatory.

---

# Business Rules

## Rule 1

Reservations never change physical inventory.

Quantity On Hand remains unchanged.

---

## Rule 2

Reservations reduce Available Quantity.

```text id="bczq4d"
Available Quantity

=

Quantity On Hand

-

Reserved Quantity
```

---

## Rule 3

A reservation belongs to exactly one Sales Order.

---

## Rule 4

A reservation belongs to exactly one Warehouse.

---

## Rule 5

A reservation belongs to exactly one SKU.

---

## Rule 6

One Sales Order may create multiple reservations.

Example:

```text id="dgjlwm"
Sales Order

↓

Bedsheet

↓

Reservation

Sales Order

↓

Comforter

↓

Reservation
```

---

## Rule 7

Reservations are temporary.

They must eventually be:

* Fulfilled
* Released
* Cancelled

---

## Rule 8

Reservations cannot exceed Available Quantity unless negative inventory is explicitly permitted by company policy.

---

## Rule 9

Dispatch automatically releases the reservation and creates the corresponding SALE Inventory Movement.

---

## Rule 10

Cancelled Sales Orders automatically release all related reservations.

---

# Relationships

Stock Reservation relates to:

* Sales Order
* Warehouse
* SKU
* Inventory Balance

---

# Lifecycle

```text id="iq59zh"
CREATED

↓

ALLOCATED

↓

FULFILLED

or

RELEASED

or

CANCELLED
```

Only ACTIVE reservations affect Available Quantity.

---

# Reservation Workflow

```text id="2s6jlwm"
Sales Order

↓

Check Available Stock

↓

Reserve Inventory

↓

Picking

↓

Packing

↓

Dispatch

↓

Release Reservation

↓

Create SALE Inventory Movement
```

---

# Reservation Release

Reservations are released when:

* Order is cancelled.
* Dispatch is completed.
* Reservation expires.
* User manually releases reservation.

Released reservations no longer affect Available Quantity.

---

# Reporting Impact

Stock Reservations contribute to:

* Reserved Stock Report
* Available Stock Report
* Order Allocation Report
* Warehouse Allocation Report
* Inventory Dashboard

---

# Examples

## Example 1

Current Stock

100

Reserved

20

```text id="0zeyvn"
Quantity On Hand

100
```

```text id="k3zfdg"
Reserved

20
```

```text id="tpmcxg"
Available

80
```

---

## Example 2

Sales Order

SO-000145

SKU

BEDSHEET-001

Quantity

5

Warehouse

Delhi

Reservation Created

5 Units Reserved

Inventory Effect

No Physical Stock Change

Available Quantity Reduced by 5

---

# Future Enhancements

Future versions may support:

* Partial reservations
* Reservation priorities
* Reservation expiry
* Auto allocation across warehouses
* AI-based reservation optimization
* Wave picking
* Pick lists

---

# Guiding Principle

**A Stock Reservation protects inventory without moving inventory.**

Reservations ensure that customer commitments are honored while preserving the integrity of physical inventory.

Physical stock changes occur only through Inventory Movements.

Reservations only affect inventory availability.
