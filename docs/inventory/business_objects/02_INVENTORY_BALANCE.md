# Inventory Balance

## Purpose

The Inventory Balance Business Object represents the current stock position of every SKU within a warehouse.

Inventory Balance is a calculated business object derived entirely from posted Inventory Movements.

It provides the real-time inventory quantities required for order allocation, warehouse operations, inventory reporting, and future accounting calculations.

Inventory Balance is never edited directly.

---

# Responsibilities

Inventory Balance is responsible for:

* Maintaining current stock position.
* Providing available inventory for order allocation.
* Tracking reserved inventory.
* Tracking warehouse-wise stock.
* Supporting inventory reports.
* Supporting inventory valuation.

Inventory Balance is **not** responsible for:

* Recording inventory transactions.
* Maintaining inventory history.
* Creating inventory movements.
* Managing warehouse transfers.
* Recording stock adjustments.

Those responsibilities belong to the Inventory Movement Business Object.

---

# Business Attributes

## Identification

| Attribute | Description   |
| --------- | ------------- |
| Warehouse | Warehouse     |
| SKU       | Inventory SKU |

Warehouse + SKU uniquely identify one Inventory Balance.

---

## Inventory Quantities

| Attribute          | Description                            |
| ------------------ | -------------------------------------- |
| Quantity On Hand   | Physical stock currently available     |
| Reserved Quantity  | Stock reserved for pending orders      |
| Available Quantity | Quantity available for new allocations |
| Incoming Quantity  | Expected inbound stock                 |
| Outgoing Quantity  | Expected outbound stock                |

---

## Cost Information

| Attribute          | Description                   |
| ------------------ | ----------------------------- |
| Average Cost       | Current weighted average cost |
| Last Purchase Cost | Most recent purchase cost     |

Future versions may support FIFO/LIFO costing.

---

## Audit Information

| Attribute          | Description                       |
| ------------------ | --------------------------------- |
| Last Movement Date | Most recent inventory transaction |
| Last Updated       | Balance calculation timestamp     |

---

# Calculation Rules

Inventory Balance is calculated from Inventory Movements.

```text id="v3egpo"
Quantity On Hand

=

Opening Stock

+

Purchases

+

Customer Returns

+

Transfer In

+

Manufacturing In

-

Sales

-

Supplier Returns

-

Transfer Out

-

Manufacturing Out

± Stock Adjustments
```

---

Reserved Quantity is calculated independently.

```text id="jjr17d"
Reserved Quantity

=

All Active Reservations
```

---

Available Quantity is calculated as:

```text id="wqexxk"
Available Quantity

=

Quantity On Hand

-

Reserved Quantity
```

---

# Validation Rules

* Warehouse is mandatory.
* SKU is mandatory.
* Quantity values cannot be null.
* Reserved Quantity cannot exceed Quantity On Hand.
* Available Quantity is always system calculated.

---

# Business Rules

## Rule 1

Inventory Balance is read-only.

Users cannot manually edit balances.

---

## Rule 2

Inventory Balance is updated only through Inventory Movements.

---

## Rule 3

Every Warehouse-SKU combination has exactly one Inventory Balance.

---

## Rule 4

Available Quantity must always be calculated.

It cannot be manually entered.

---

## Rule 5

Negative inventory is controlled by company policy.

Future versions may allow or prohibit negative inventory based on configuration.

---

## Rule 6

Cancelled Inventory Movements do not affect Inventory Balance.

---

## Rule 7

Only POSTED Inventory Movements contribute to Inventory Balance.

---

# Relationships

Inventory Balance relates to:

* Warehouse
* SKU
* Inventory Movements
* Stock Reservations

---

# Lifecycle

Inventory Balance does not have a traditional lifecycle.

It is continuously recalculated whenever posted Inventory Movements or active Reservations change.

---

# Inventory Availability

The Inventory Engine exposes three inventory values.

## Quantity On Hand

Physical inventory currently present.

---

## Reserved Quantity

Inventory committed to open orders.

---

## Available Quantity

Inventory that may be allocated to new orders.

---

# Reporting Impact

Inventory Balance contributes to:

* Current Stock Report
* Warehouse Inventory Report
* SKU Availability Report
* Low Stock Report
* Inventory Valuation Report
* Inventory Dashboard

---

# Examples

## Example 1

Opening Stock

100

Sales

20

Customer Returns

5

Reservations

15

```text id="iijjkr"
Quantity On Hand

100

-

20

+

5

=

85
```

```text id="8n0sdc"
Reserved Quantity

15
```

```text id="yopvly"
Available Quantity

85

-

15

=

70
```

---

## Example 2

Warehouse A

SKU

BEDSHEET-001

```text id="q5n7nk"
Quantity On Hand

250

Reserved

40

Available

210
```

Warehouse B

SKU

BEDSHEET-001

```text id="kx4fwm"
Quantity On Hand

90

Reserved

10

Available

80
```

Global Inventory

```text id="tnyr0l"
Quantity On Hand

340

Reserved

50

Available

290
```

---

# Future Enhancements

Future versions may support:

* Real-time inventory snapshots
* Multi-company inventory balances
* Batch-wise balances
* Serial number balances
* Warehouse zones
* Bin locations
* AI inventory forecasting

---

# Guiding Principle

**Inventory Balance is always a calculated result, never a manually maintained value.**

Inventory Movements are the system of record.

Inventory Balance is the current view of those recorded business events.
