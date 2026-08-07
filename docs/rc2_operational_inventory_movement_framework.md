# Operational Inventory Movement Framework (RC2)

## AaramBooks Inventory Truth Engine

---

# Executive Summary

The **Operational Inventory Movement Framework (RC2)** has been successfully implemented.

This milestone expands the Inventory Truth Engine beyond sales-driven inventory and enables it to understand the major operational events that occur throughout the lifecycle of physical inventory.

The Inventory Engine now records business events instead of simply maintaining stock balances.

Every inventory-affecting operation is translated into immutable Inventory Movements, ensuring complete explainability, auditability, and deterministic balance reconstruction.

---

# Vision

Inventory should never change because a quantity was edited.

Inventory changes because a business event occurred.

Examples include:

* Goods received from a supplier
* Goods returned to a supplier
* Customer returned merchandise
* Shipment returned by courier (RTO)
* Manual stock correction
* Physical stock count adjustment

The Operational Inventory Movement Framework teaches the Inventory Truth Engine to understand these real-world business events.

---

# Architectural Philosophy

The Inventory Truth Engine follows a strict event-driven architecture.

```text
Business Event
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
Inventory Exceptions
        │
        ▼
Inventory Confidence
```

Every physical inventory change begins as a business event.

Inventory quantities are never edited directly.

---

# Objectives

RC2 introduces operational completeness for physical inventory.

Supported inventory operations now include:

* Purchase Receipts
* Purchase Returns
* Customer Returns
* RTO Returns
* Manual Adjustments
* Physical Stock Count Adjustments

The focus of RC2 is physical stock movement only.

Inventory valuation and accounting remain intentionally outside the scope of this release.

---

# Movement Type Standardization

A strict movement type definition has been introduced to guarantee consistency throughout the system.

Supported movement types:

* OPENING_STOCK
* PURCHASE_RECEIPT
* PURCHASE_RETURN
* SALES_FULFILLMENT
* CUSTOMER_RETURN
* RTO_RETURN
* MANUAL_ADJUSTMENT
* STOCK_COUNT_ADJUSTMENT

These movement types now represent the official language of the Inventory Truth Engine.

---

# Business APIs

Rather than exposing a generic inventory mutation endpoint, RC2 introduces business-oriented APIs.

Implemented endpoints:

```text
POST /api/v1/inventory/movements/purchase-receipts

POST /api/v1/inventory/movements/purchase-returns

POST /api/v1/inventory/movements/customer-returns

POST /api/v1/inventory/movements/rto-returns

POST /api/v1/inventory/movements/manual-adjustments

POST /api/v1/inventory/movements/stock-counts
```

Each endpoint represents a real operational workflow instead of a database operation.

---

# Processing Lifecycle

Each endpoint follows the same deterministic workflow.

```text
API Request
        │
        ▼
Validation
        │
        ▼
Business Service
        │
        ▼
Inventory Movement
        │
        ▼
Inventory Ledger
        │
        ▼
Balance Calculator
        │
        ▼
Inventory Balance Projection
        │
        ▼
Inventory Exception Detection
        │
        ▼
Inventory Confidence Update
```

Every operational event produces the same predictable processing pipeline.

---

# Purchase Receipt

A Purchase Receipt increases physical inventory.

```text
Purchase Receipt

↓

Inventory +
```

Future versions may insert Quality Control between receipt and inventory availability, but RC2 records receipts directly.

---

# Purchase Return

Returning inventory to a supplier reduces available stock.

```text
Purchase Return

↓

Inventory -
```

Each movement references the originating purchase document.

---

# Customer Return

Customer Returns increase physical inventory after goods are received.

```text
Customer Return

↓

Inventory +
```

Customer Returns remain distinct from RTO Returns to preserve operational history.

---

# RTO Return

Return-to-Origin inventory follows a separate operational workflow.

```text
Courier

↓

Warehouse

↓

Inventory +
```

Although both Customer Returns and RTO Returns increase inventory, they represent different business events and are stored independently.

---

# Manual Adjustment

Manual inventory corrections are treated as exceptional events.

Every manual adjustment records:

* SKU
* Warehouse
* Quantity
* Adjustment Date
* Reference Number
* Reason

This creates a permanent audit trail for inventory corrections.

---

# Stock Count Adjustment

Physical stock counts do not overwrite inventory.

Instead:

```text
Physical Count

↓

Difference

↓

STOCK_COUNT_ADJUSTMENT

↓

Inventory Movement
```

This preserves complete explainability.

---

# Inventory Ledger

Every operational event immediately extends the Inventory Ledger.

Example:

```text
Opening Stock          +30
Purchase Receipt       +50
Sale                  -12
Customer Return        +2
Purchase Return        -5
Manual Adjustment      -1

Closing Balance        64
```

Every unit can now be traced back to the originating business event.

---

# Inventory Balance

Inventory Balance continues to function as a projection.

It is never edited directly.

Instead:

```text
Inventory Movements

↓

Inventory Ledger

↓

Inventory Balance
```

The Balance Calculator remains purely mathematical.

---

# Inventory Exceptions

RC2 integrates operational movements with the Inventory Exception framework.

Examples include:

* Negative Inventory
* Duplicate Movements
* Invalid References

Operational inconsistencies become explicit exceptions rather than silent corrections.

---

# Inventory Confidence

Although the Confidence Engine remains unchanged in RC2, the new operational movements provide richer inputs for future confidence calculations.

Examples:

| Event                | Confidence Effect |
| -------------------- | ----------------- |
| Purchase Receipt     | Positive          |
| Customer Return      | Positive          |
| Physical Stock Count | Strong Positive   |
| Manual Adjustment    | Negative          |
| Negative Inventory   | Negative          |

This lays the foundation for explainable inventory reliability metrics.

---

# Verification

RC2 was validated through end-to-end testing.

A backend integration test confirmed that:

* Manual Adjustment API accepted valid requests.
* Inventory Movement was created successfully.
* Inventory Ledger was updated.
* Balance Calculator recalculated projected stock.
* Inventory Balance reflected the expected quantity.

The complete operational workflow executed successfully without bypassing the Inventory Truth Engine.

---

# Relationship with Existing Components

RC2 builds upon previously completed milestones:

* Inventory Truth Engine
* Inventory Ledger
* Inventory Balance Projection
* Inventory Exception Framework
* Inventory Confidence Framework
* Inventory Truth Certification Suite

No architectural redesign was required.

The new movement types integrate directly into the existing event-driven model.

---

# Current Scope

RC2 intentionally excludes:

* Inventory Valuation
* Cost of Goods Sold (COGS)
* Accounts Payable
* Purchase Accounting
* Landed Cost Allocation
* Financial Posting Rules

These concerns remain part of the Accounting Engine and future releases.

---

# Future Roadmap

With operational inventory movements complete, the next development phase is **RC3 – Warehouse Operations**.

Planned features include:

* Multi-Warehouse Support
* Warehouse Transfers
* Warehouse Ledger
* Warehouse Balances
* Bin Locations
* In-Transit Inventory

Subsequent releases will introduce:

* Quality Control
* Reserved Inventory
* Pick & Pack Workflows
* Inventory Reservations
* Available-to-Promise (ATP)
* Inventory Forecasting

Each release will extend the Inventory Truth Engine while preserving its event-driven architecture.

---

# Final Conclusion

The completion of the Operational Inventory Movement Framework marks a significant evolution of the Inventory Truth Engine.

AaramBooks no longer understands only sales-driven inventory changes.

It now understands the major operational events that occur throughout the physical lifecycle of inventory.

Every purchase, return, adjustment, and stock count is transformed into immutable Inventory Movements, extending the Inventory Ledger and updating projected balances without sacrificing explainability.

Together with the Inventory Truth Certification Suite, this milestone establishes a production-ready operational foundation upon which future warehouse management, quality control, reservations, and advanced inventory analytics can be confidently built.

The Inventory Truth Engine is no longer just calculating stock.

It is now modelling the real-world operational behavior of inventory.
