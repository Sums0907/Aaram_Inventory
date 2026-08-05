# Inventory Engine

## Purpose

The Inventory Engine is responsible for maintaining the physical stock position of every SKU across all warehouses.

Unlike traditional ERP systems that directly update stock quantities, the Inventory Engine treats every inventory change as an immutable business event called an **Inventory Movement**.

Current stock is always derived from these movements, ensuring complete traceability, auditability, and consistency.

The Inventory Engine is the authoritative source for inventory information within AaramBooks.

---

# Position in System Architecture

```
External Platforms
        │
        ▼
Data Ingestion
        │
        ▼
Operations Domain
        │
        ▼
Matching Domain
        │
        ▼
=====================
 Inventory Engine
=====================
        │
        ├────────► Accounting Engine
        ├────────► Reporting Engine
        └────────► Future Automation
```

---

# Responsibilities

The Inventory Engine is responsible for:

* Maintaining inventory balances
* Recording inventory movements
* Managing warehouse-wise stock
* Managing stock reservations
* Recording stock adjustments
* Recording warehouse transfers
* Maintaining complete inventory history
* Providing real-time inventory availability

The Inventory Engine is NOT responsible for:

* Importing CSV files
* Matching business documents
* Customer management
* Supplier management
* Accounting journals
* GST calculations
* Payment reconciliation

---

# Core Principles

The Inventory Engine follows five fundamental principles.

## 1. Inventory is Event Driven

Inventory never changes directly.

Every stock change must originate from an Inventory Movement.

Examples:

* Opening Stock
* Sale
* Purchase
* Customer Return
* Supplier Return
* Warehouse Transfer
* Stock Adjustment
* Manufacturing
* Stock Reservation Release

---

## 2. Inventory Movements are Immutable

Once created, an Inventory Movement cannot be modified.

Corrections must always be recorded as new movements.

This guarantees complete auditability.

---

## 3. Inventory Balance is Calculated

Current stock is never manually maintained.

It is always calculated from all historical inventory movements.

```
Inventory Balance

=

Opening Stock

+

Purchases

+

Returns

-

Sales

-

Transfers Out

+

Transfers In

± Adjustments
```

---

## 4. Warehouse is Mandatory

Every inventory movement belongs to exactly one warehouse.

Inventory is always maintained warehouse-wise.

Global inventory is derived by summing warehouse balances.

---

## 5. SKU is Mandatory

Every inventory movement references exactly one SKU.

Inventory is never maintained at the Product level.

The SKU is the smallest inventory unit.

---

# Business Objects

## Inventory Movement

Represents one immutable stock transaction.

Examples:

* Opening Stock
* Sale
* Purchase
* Return
* Transfer
* Adjustment
* Reservation
* Reservation Release

---

## Inventory Balance

Represents the current calculated stock position.

Fields:

* Warehouse
* SKU
* Quantity On Hand
* Reserved Quantity
* Available Quantity
* Last Updated

Inventory Balance may be stored as a materialized view or cache for performance, but Inventory Movement remains the system of record.

---

## Stock Reservation

Represents inventory temporarily reserved for an order.

Reserved stock is unavailable for other orders until released or fulfilled.

---

## Stock Transfer

Represents movement of inventory between warehouses.

A transfer creates two inventory movements:

* Transfer Out
* Transfer In

The total inventory remains unchanged.

---

## Stock Adjustment

Represents manual corrections to inventory.

Examples:

* Physical stock count
* Damaged goods
* Lost inventory
* Excess inventory

Every adjustment requires:

* Reason
* User
* Timestamp

---

# Inventory Movement Types

The engine supports the following movement types.

```
OPENING_STOCK

PURCHASE

PURCHASE_RETURN

SALE

CUSTOMER_RETURN

TRANSFER_IN

TRANSFER_OUT

STOCK_ADJUSTMENT

RESERVATION

RESERVATION_RELEASE

MANUFACTURING_IN

MANUFACTURING_OUT
```

Additional movement types may be introduced without changing the overall architecture.

---

# Inventory Workflow

```
Business Event

↓

Inventory Movement

↓

Inventory Ledger

↓

Inventory Balance

↓

Inventory Availability
```

---

# Inventory Status

Each Inventory Movement may have one of the following statuses.

```
PENDING

POSTED

CANCELLED
```

Only POSTED movements affect inventory balances.

---

# Reservation Workflow

```
Sales Order

↓

Reserve Stock

↓

Inventory Reserved

↓

Invoice Generated

↓

Dispatch

↓

Reservation Released

↓

Sale Movement Posted
```

---

# Warehouse Transfers

```
Warehouse A

↓

Transfer Out

↓

In Transit

↓

Transfer In

↓

Warehouse B
```

Both movements must reference the same transfer document.

---

# Stock Availability

Available Quantity is calculated as:

```
Available Quantity

=

Quantity On Hand

-

Reserved Quantity
```

Users should always see Available Quantity when allocating inventory.

---

# Inventory Reports

The Inventory Engine provides the following reports:

* Current Inventory
* Warehouse Stock Summary
* SKU Stock Summary
* Inventory Ledger
* Inventory Movement History
* Reserved Stock Report
* Low Stock Report
* Negative Stock Report
* Stock Adjustment Report
* Transfer Report

---

# Events

The Inventory Engine publishes business events.

Examples:

```
InventoryMovementCreated

InventoryReserved

InventoryReleased

InventoryTransferred

InventoryAdjusted

InventoryBalanceUpdated
```

Future domains subscribe to these events.

* Accounting Engine
* Reporting Engine
* Automation Engine

---

# Design Principles

The Inventory Engine must always be:

* Deterministic
* Auditable
* Event Driven
* Idempotent
* Warehouse Aware
* SKU Centric
* Immutable

Inventory quantities must never be edited directly.

Every inventory change must be traceable back to an Inventory Movement.

---

# Future Roadmap

## Version 1

* Inventory Movements
* Inventory Balance
* Reservations
* Transfers
* Adjustments

## Version 2

* Purchase Receipts
* Batch Tracking
* Serial Number Tracking
* Multi-location Fulfilment

## Version 3

* Manufacturing
* Bill of Materials (BOM)
* Production Orders
* Work Orders

## Version 4

* Demand Forecasting
* Auto Reorder Suggestions
* Warehouse Optimization

## Version 5

* AI-powered Inventory Planning
* Predictive Stock Allocation
* Smart Procurement Recommendations


# Domain Lifecycle

The Inventory Engine does not operate independently. It consumes business events from upstream domains and produces inventory events that are consumed by downstream domains.

The lifecycle below illustrates how a customer order ultimately affects inventory.

---

## Standard Sales Flow

```text
Customer Places Order
            │
            ▼
     Sales Order Created
      (Operations Domain)
            │
            ▼
     Documents Matched
      (Matching Domain)
            │
            ▼
     Inventory Reserved
     (Inventory Engine)
            │
            ▼
      Order Dispatched
            │
            ▼
 Inventory Movement Created
        (SALE)
            │
            ▼
 Reservation Released
            │
            ▼
 Inventory Balance Updated
            │
            ▼
 Accounting Event Generated
     (Accounting Engine)
            │
            ▼
     Journal Exported
      (Vyapar Export)
```

---

## Customer Return Flow

```text
Customer Return
        │
        ▼
Return Approved
        │
        ▼
Inventory Movement Created
   (CUSTOMER_RETURN)
        │
        ▼
Inventory Balance Updated
        │
        ▼
Credit Note Generated
(Accounting Engine)
```

---

## Purchase Flow (Future)

```text
Purchase Receipt
        │
        ▼
Goods Received
        │
        ▼
Inventory Movement Created
     (PURCHASE)
        │
        ▼
Inventory Balance Updated
        │
        ▼
Purchase Accounting
```

---

## Warehouse Transfer Flow

```text
Warehouse Transfer Requested
              │
              ▼
Transfer Out Movement
              │
              ▼
Inventory In Transit
              │
              ▼
Transfer In Movement
              │
              ▼
Destination Warehouse Updated
```

---

## Stock Adjustment Flow

```text
Physical Stock Count
          │
          ▼
Difference Identified
          │
          ▼
Stock Adjustment Created
          │
          ▼
Inventory Movement Posted
          │
          ▼
Inventory Balance Updated
```

---

# Inventory Event Pipeline

Every inventory change follows the same internal pipeline.

```text
Business Event
      │
      ▼
Business Validation
      │
      ▼
Inventory Movement
      │
      ▼
Inventory Ledger
      │
      ▼
Inventory Balance
      │
      ▼
Inventory Availability
      │
      ▼
Business Events Published
```

The Inventory Engine never updates stock quantities directly.

Every stock change must first become an Inventory Movement.

Inventory Balance is always derived from the Inventory Ledger.

---

# Interaction with Other Domains

## Operations Domain

Produces business documents that may create inventory movements.

Examples:

* Sales Order
* Sales Return
* Purchase Receipt (Future)

---

## Matching Domain

Confirms relationships between business documents before inventory is affected.

Examples:

* Sales Order matched to Tax Invoice
* Payment matched to Settlement

---

## Inventory Domain

Creates and maintains:

* Inventory Movements
* Inventory Ledger
* Inventory Balances
* Stock Reservations
* Warehouse Transfers
* Stock Adjustments

---

## Accounting Domain

Consumes inventory events to generate accounting entries.

Examples:

* Cost of Goods Sold (COGS)
* Inventory Asset Adjustments
* Stock Loss
* Stock Gain

---

## Reporting Domain

Reads inventory data without modifying it.

Examples:

* Current Stock Report
* Inventory Ledger
* Warehouse Stock Report
* Low Stock Report
* Inventory Valuation
* Slow Moving Inventory
* Dead Stock Analysis

---

# Design Principle

Every business process eventually becomes an Inventory Movement.

The Inventory Movement is the single source of truth for all stock changes.

Inventory Balance is a calculated result—not a manually maintained value.

This event-driven approach guarantees complete auditability, deterministic calculations, and a scalable foundation for future capabilities such as manufacturing, demand forecasting, and AI-powered inventory optimization.
