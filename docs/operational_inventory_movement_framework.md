# Operational Inventory Movement Framework

## AaramBooks Inventory Truth Engine

---

# Executive Summary

With the Inventory Truth Engine and Inventory Truth Certification Suite complete, the next phase of AaramBooks is to expand the engine's understanding of real-world inventory operations.

Until now, the engine has successfully explained inventory changes caused by sales.

This phase extends the engine to understand every major operational event that affects physical stock.

The objective is **not** to introduce inventory valuation or accounting entries.

The objective is to ensure that every physical change in inventory is represented by deterministic Inventory Movements.

---

# Vision

The Inventory Truth Engine should never directly manipulate stock quantities.

Instead, it should record business events.

Every business event produces one or more immutable Inventory Movements.

Inventory Balance is always derived from these movements.

---

# Philosophy

Inventory does not change because someone edits a quantity.

Inventory changes because something happened.

Examples:

* Goods were received.
* Goods were returned.
* Customer returned a product.
* Physical stock was counted.
* Inventory was manually adjusted.

The Inventory Truth Engine records these events and explains their impact.

---

# Objectives

Expand the Inventory Truth Engine to support the remaining operational inventory events.

These include:

* Purchase Receipts
* Purchase Returns
* Customer Returns
* RTO Returns
* Manual Adjustments
* Physical Stock Count Adjustments

Each event becomes a first-class business object within AaramBooks.

---

# Design Principles

## Business-Driven APIs

The API should expose business operations rather than low-level inventory mutations.

Preferred API structure:

```text
POST /inventory/purchase-receipts

POST /inventory/purchase-returns

POST /inventory/customer-returns

POST /inventory/rto-returns

POST /inventory/manual-adjustments

POST /inventory/stock-counts
```

The API communicates business intent.

Internally, each endpoint generates one or more Inventory Movements.

---

## Inventory Movements are Internal

External users should never create Inventory Movements directly.

Instead:

```text
Business Event

↓

Business Service

↓

Inventory Movement

↓

Inventory Ledger

↓

Inventory Balance
```

Inventory Movements remain an internal implementation detail.

---

# Supported Movement Types

The Inventory Engine will support the following canonical movement types.

| Movement Type          | Inventory Effect    |
| ---------------------- | ------------------- |
| OPENING_STOCK          | Increase            |
| PURCHASE_RECEIPT       | Increase            |
| PURCHASE_RETURN        | Decrease            |
| SALES_FULFILLMENT      | Decrease            |
| CUSTOMER_RETURN        | Increase            |
| RTO_RETURN             | Increase            |
| MANUAL_ADJUSTMENT      | Increase / Decrease |
| STOCK_COUNT_ADJUSTMENT | Increase / Decrease |

These movement types become the official vocabulary of the Inventory Truth Engine.

---

# Customer Return vs RTO Return

Although both increase inventory, they represent different business events.

## Customer Return

```text
Customer

↓

Return Approved

↓

Warehouse Receives Product

↓

Quality Inspection

↓

Inventory +
```

---

## RTO Return

```text
Courier

↓

Delivery Failed

↓

Parcel Returned

↓

Warehouse Receives Product

↓

Quality Inspection

↓

Inventory +
```

Keeping these movement types separate preserves operational accuracy and enables future analytics.

---

# Purchase Receipt

Receiving inventory is treated as a business event.

```text
Purchase Receipt

↓

Inventory +
```

Future versions may introduce:

```text
Goods Received

↓

Quality Inspection

↓

Accepted

↓

Inventory
```

For Version 1, a Purchase Receipt directly increases stock.

---

# Purchase Return

Returning goods to a supplier reduces physical inventory.

Workflow:

```text
Purchase Return

↓

Inventory -
```

Every Purchase Return should reference:

* Vendor
* Purchase Document
* SKU
* Quantity

---

# Manual Adjustment

Manual adjustments should always be exceptional.

Every manual adjustment must require:

* Quantity
* Adjustment Direction
* Reason
* User
* Reference Number

Example:

```text
Adjustment

-3

Reason

Damaged During Handling

Reference

MAN-2026-001
```

Manual adjustments become part of the permanent audit trail.

---

# Physical Stock Count

A physical stock count should never directly overwrite inventory.

Instead:

```text
Physical Count

↓

System Quantity

↓

Difference

↓

Stock Count Adjustment

↓

Inventory Movement
```

Example

System Quantity:

```text
100
```

Physical Count:

```text
97
```

Difference:

```text
-3
```

Generated Movement:

```text
STOCK_COUNT_ADJUSTMENT

-3
```

This preserves complete explainability.

---

# Inventory Ledger

Every operational event immediately extends the Inventory Ledger.

Example:

```text
Opening Stock

+30

Purchase Receipt

+50

Sale

-10

Customer Return

+2

Purchase Return

-5

Manual Adjustment

-1

Closing Balance

66
```

Every balance remains fully explainable.

---

# Inventory Balance

Inventory Balance continues to be a projection.

It is never edited manually.

Instead:

```text
Inventory Movements

↓

Inventory Ledger

↓

Inventory Balance
```

The Balance Calculator remains responsible only for mathematical projection.

---

# Inventory Exceptions

When operational events produce impossible inventory states:

Examples:

* Negative Inventory
* Duplicate Movements
* Invalid References

The Inventory Exception framework records these situations without modifying inventory.

---

# Inventory Confidence

Operational events also influence Inventory Confidence.

Examples:

| Event                | Confidence Impact |
| -------------------- | ----------------- |
| Purchase Receipt     | Positive          |
| Customer Return      | Positive          |
| Physical Stock Count | Strong Positive   |
| Manual Adjustment    | Negative          |
| Negative Inventory   | Negative          |
| Duplicate Movement   | Negative          |

Confidence continues to explain the reliability of inventory rather than changing inventory itself.

---

# API Workflow

Every endpoint follows the same lifecycle.

```text
Business Request

↓

Validation

↓

Business Service

↓

Inventory Movement

↓

Inventory Ledger

↓

Balance Projection

↓

Inventory Exception Check

↓

Inventory Confidence Update
```

This guarantees consistency across all operational workflows.

---

# Certification Expansion

The Inventory Truth Certification Suite will grow alongside the engine.

Current certification verifies:

* Opening Stock
* Sales

Future certification scenarios include:

### Scenario 1

Opening Stock

↓

Sales

---

### Scenario 2

Opening Stock

↓

Purchase Receipt

↓

Sales

---

### Scenario 3

Opening Stock

↓

Sales

↓

Customer Return

---

### Scenario 4

Opening Stock

↓

Purchase Receipt

↓

Purchase Return

↓

Sales

---

### Scenario 5

Opening Stock

↓

Physical Stock Count

↓

Stock Count Adjustment

---

Eventually the certification suite will validate the complete inventory lifecycle.

---

# Current Scope

This phase intentionally excludes:

* Inventory Valuation
* Cost of Goods Sold
* Accounts Payable
* Inventory Accounting Journals
* Landed Cost Allocation

The focus remains exclusively on physical inventory quantities.

---

# Future Roadmap

Following completion of operational movement types, future development will focus on:

### RC2

Operational Inventory

* Purchase Receipts
* Purchase Returns
* Customer Returns
* RTO Returns
* Manual Adjustments
* Stock Count Adjustments

### RC3

Warehouse Operations

* Multi-Warehouse
* Transfer In
* Transfer Out
* Warehouse Ledger

### RC4

Quality Control

* QC Hold
* QC Release
* Damaged Inventory
* Scrap

### RC5

Inventory Reservation

* Reserved Inventory
* Available Inventory
* Pick Lists
* Packing
* Dispatch

Each release extends the Inventory Truth Engine without changing its architectural principles.

---

# Final Philosophy

The Operational Inventory Movement Framework is not simply a collection of APIs.

It is the process through which the Inventory Truth Engine learns to understand real-world inventory operations.

Every purchase, return, adjustment, transfer, or stock count becomes a business event that is permanently recorded as immutable Inventory Movements.

These movements explain the Inventory Ledger.

The Inventory Ledger explains the Inventory Balance.

The Inventory Balance feeds Inventory Confidence.

Together they ensure that AaramBooks can answer not only **"How much inventory do I have?"**, but also **"Why do I have this inventory?"** and **"How confidently can I trust these numbers?"**

This framework transforms the Inventory Truth Engine from a sales-driven stock tracker into a comprehensive operational inventory platform capable of explaining every physical movement of inventory throughout its lifecycle.
