# Inventory Engine Vision

## Primary Objective

The primary objective of the AaramBooks Inventory Engine is to ensure that, for every SKU, AaramBooks can produce a complete, accurate, and fully auditable Inventory Ledger that explains the current stock balance from the opening stock to the present date.

Unlike traditional inventory systems that simply maintain stock quantities, AaramBooks must be able to explain **why** the current inventory exists by recording every business event that changed it.

Every inventory balance should be completely traceable to its underlying inventory movements.

---

# Design Constraints

The Inventory Engine shall achieve this objective while addressing the operational realities of Indian e-commerce businesses identified during the initial design of AaramBooks.

These include, but are not limited to:

* Marketplace inventory is not the source of truth for physical inventory.
* Purchase invoices are frequently delayed, consolidated, or lack SKU-level details.
* Physical inventory may exist before accounting documents are received.
* Multiple sales channels (ShopDeck, offline sales, future marketplaces) must share a single inventory source of truth.
* Inventory changes occur due to numerous operational events beyond sales and purchases, including returns, replacements, damages, transfers, quality checks, and manual adjustments.
* Physical stock, accounting records, and marketplace listings may temporarily diverge and must be reconciled without compromising auditability.
* Every inventory movement must remain traceable to its originating business document wherever possible.
* The system must support gradual reconciliation of imperfect real-world data instead of assuming ideal business processes.

---

# Guiding Philosophy

AaramBooks does not attempt to model an ideal warehouse.

It models the real operational behaviour of Indian e-commerce businesses.

The Inventory Engine must therefore prioritise:

* Accuracy over assumptions.
* Auditability over convenience.
* Explainability over simple quantity tracking.
* Deterministic business rules over manual corrections.
* Progressive reconciliation of imperfect business data.

---

# Success Criteria

The Inventory Engine will be considered successful when, for any SKU and any date, it can answer the following questions with complete confidence:

* What is the current physical stock?
* Why is this the current stock?
* Which business events created every inventory movement?
* Which source documents support those movements?
* Which movements remain provisional due to missing or delayed documentation?
* What differences exist between physical inventory, marketplace inventory, and accounting records, and why?
* Can the complete inventory history be reconstructed from the Inventory Ledger without ambiguity?

Only when these questions can be answered consistently and deterministically should the Inventory Engine be considered the authoritative source of inventory truth within AaramBooks.


# Inventory Engine (Version 1)

## Vision

The Inventory Engine is the operational heart of AaramBooks.

Its objective is **not** to maintain inventory quantities. Its objective is to establish the **authoritative truth of physical inventory** for an Indian e-commerce business operating under imperfect real-world conditions.

Unlike conventional inventory systems that assume perfect purchasing, warehousing, and accounting processes, AaramBooks acknowledges that inventory data is often incomplete, delayed, or inconsistent. The Inventory Engine is therefore designed to progressively reconcile these realities while maintaining complete auditability.

---

# Primary Objective

For every SKU, AaramBooks shall produce a complete, accurate, and fully auditable **Inventory Ledger** that explains the current stock balance from the opening stock to the present date.

The Inventory Engine must answer not only **"How much stock exists?"** but also **"Why does this stock exist?"**

Every inventory balance must be traceable back to the business events that created it.

---

# Core Philosophy

Inventory should never be managed as a simple quantity.

Instead, inventory should be managed as a history of business events.

Just as Accounting derives Ledger Balances from Journal Entries, Inventory derives Inventory Balances from Inventory Movements.

```text
Journal Entries
        ↓
Ledger Balance

Inventory Movements
        ↓
Inventory Balance
```

Inventory Balance is therefore a **projection**, never the primary source of truth.

---

# Real-World Design Constraints

The Inventory Engine has been designed specifically around the operational realities of Indian e-commerce businesses.

## Marketplace Inventory is not Physical Inventory

Marketplace inventory exists only to facilitate selling.

It is not the source of truth.

Examples:

* ShopDeck
* Amazon
* Future marketplaces

must all consume inventory rather than define it.

---

## Purchase Documentation is Imperfect

Suppliers frequently:

* deliver inventory before invoices,
* raise consolidated invoices,
* omit SKU-level information,
* use generic descriptions.

The Inventory Engine must therefore allow inventory to exist before accounting documents arrive.

---

## Physical Inventory and Accounting are Independent

Inventory answers:

* What physically exists?

Accounting answers:

* What financially happened?

Both systems must remain synchronized without becoming dependent upon one another.

---

## Inventory Changes for Many Reasons

Inventory movements are created by far more than purchases and sales.

Examples include:

* Purchase
* Sale
* Customer Return
* Replacement
* Damage
* Transfer
* Manual Adjustment
* Stock Correction
* Quality Check
* Write-Off

Every movement must remain auditable.

---

# Guiding Principles

## Movement First

Inventory quantities are never updated directly.

Every stock change is represented by an Inventory Movement.

Inventory Balance is calculated from those movements.

---

## Explainability

Every inventory figure should be explainable.

The system must always answer:

* Why is this stock available?
* Which document created it?
* Which movement reduced it?
* Which adjustment changed it?

---

## Auditability

Every movement should reference its originating business document whenever possible.

Examples:

* Purchase Invoice
* Sales Order
* Tax Invoice
* Return
* Adjustment Note

---

## Progressive Reconciliation

The Inventory Engine must gracefully handle delayed documentation rather than assuming perfect business processes.

Missing information should reduce confidence—not corrupt inventory.

---

# Central Business Object

The entire Inventory Engine revolves around one immutable business object.

```
Inventory Movement
```

Examples:

* Opening Stock
* Purchase
* Sale
* Return
* Replacement
* Damage
* Adjustment
* Transfer
* QC Release

Nothing should bypass Inventory Movement.

---

# Inventory Ledger

Every SKU shall maintain a complete Inventory Ledger.

Example:

```text
Blue Bay Stripes

Opening Stock       +100

Purchase             +50

Sale                 -12

Sale                 -5

Customer Return      +2

Adjustment           -1

--------------------------------

Closing Stock       134
```

This ledger becomes the inventory equivalent of a General Ledger.

---

# Inventory Balance

Inventory Balance is a projection generated from Inventory Movements.

```
Inventory Movements

↓

Inventory Ledger

↓

Inventory Balance
```

Inventory Balance must never be manually edited.

---

# Inventory Verification

The Inventory Engine must continuously verify inventory correctness.

Examples:

Accounting Purchased      500

Inventory Received        480

Difference                20

---

Marketplace Stock         125

Inventory Stock           120

Difference                 5

---

Physical Count            118

Inventory Balance         121

Difference                 3

Differences should generate Inventory Exceptions rather than silently modifying stock.

---

# Inventory Reconciliation

Inventory and Accounting may legitimately diverge temporarily.

Example:

Supplier delivers goods

↓

Inventory Received

↓

Goods Sold

↓

Supplier Invoice Received Later

↓

Accounting Updated

The system must reconcile these differences over time without compromising auditability.

---

# Inventory States

Inventory is more than simply "Available."

Every unit may exist in one of several operational states.

Examples:

* Available
* Reserved
* Allocated
* Packed
* Shipped
* Delivered
* Returned
* Under Inspection
* Damaged
* Blocked
* Lost

State transitions occur through Inventory Movements.

---

# Reservations

Reserved stock should reduce sellable inventory without reducing physical inventory.

Examples:

* Website Order
* Instagram Order
* Wholesale Order
* Replacement Order

---

# Returns Workflow

Returns should not immediately increase sellable inventory.

Workflow:

```text
Customer Return

↓

Inspection

↓

Quality Check

↓

Available

or

↓

Damaged
```

---

# Multi-Location Design

Inventory belongs to Locations rather than hardcoded warehouses.

Examples:

* Main Warehouse
* Secondary Warehouse
* Job Worker
* Retail Store
* Third-Party Logistics

The architecture should remain location-agnostic.

---

# Batch Support

The Inventory Engine should support batch-level tracking.

Benefits include:

* Supplier Traceability
* Manufacturing Tracking
* Batch Recall
* Batch Profitability

Serial numbers are intentionally excluded as they are unnecessary for home textile products.

---

# Inventory Confidence

Inventory Confidence is a core business metric representing how trustworthy the inventory balance is for a given SKU, warehouse, or the entire business.

Unlike traditional systems that only report stock quantities, AaramBooks reports both the quantity and the confidence in that quantity.

Example:

```text
Blue Bay Stripes

Current Stock

128

Inventory Confidence

96%
```

---

## Confidence Principles

Inventory Confidence should be rule-based rather than purely mathematical.

Typical positive indicators include:

* All purchases verified.
* All sales reconciled.
* Marketplace synchronized.
* Recent physical verification completed.
* No unresolved adjustments.

Typical negative indicators include:

* Purchase invoice pending.
* Physical verification overdue.
* Pending Quality Control.
* Manual adjustments awaiting approval.
* Inventory variances.
* Marketplace discrepancies.

The system must always explain the confidence score rather than displaying only a percentage.

Example:

```text
Inventory Confidence

92%

Reasons

✓ Sales reconciled

✓ Purchases verified

✓ Marketplace synchronized

⚠ Physical verification overdue

⚠ Two returned units awaiting QC
```

---

# Inventory Truth Engine

The first release of the Inventory Engine is not an Inventory Management System.

It is an **Inventory Truth Engine**.

Its purpose is to explain every unit of inventory.

For every SKU, the system must answer:

* What is the current stock?
* Why is this the current stock?
* Which movements created this balance?
* Which documents support those movements?
* Which movements remain provisional?
* What differences exist between physical inventory, marketplace inventory, and accounting?
* How confident are we that this inventory is correct?

Only after these questions can be answered consistently should advanced inventory functionality be introduced.

---

# Implementation Roadmap

## RC1 — Inventory Truth Engine

Objective:

Explain every SKU's closing stock.

Deliverables:

* Inventory Movement
* Inventory Ledger
* Inventory Balance
* Inventory Verification

Success Criteria:

Every unit of inventory is explainable.

---

## RC2 — Inventory Ledger

Objective:

Maintain a complete movement history for every SKU.

Success Criteria:

Every inventory change is traceable.

---

## RC3 — Inventory Verification

Objective:

Automatically detect and explain inventory inconsistencies.

Success Criteria:

Inventory Exceptions generated instead of silent corrections.

---

## RC4 — Inventory Reconciliation

Objective:

Support temporary divergence between inventory and accounting while preserving correctness.

Success Criteria:

Delayed documentation reconciles cleanly.

---

## RC5 — Operational Inventory

Objective:

Support reservations, operational states, and fulfillment lifecycle.

---

## Version 2

Advanced capabilities:

* Multi-Warehouse
* Batch Management
* Transfers
* Bundle Handling
* Forecasting
* Reorder Planning
* Inventory Analytics
* Profitability by SKU

---

# Success Criteria

The Inventory Engine will be considered successful when, for any SKU and any point in time, AaramBooks can produce an Inventory Ledger that completely explains the current stock balance while accurately reflecting the realities of Indian business operations.

The final outcome is not merely inventory management.

It is **Inventory Truth**.

Just as the Accounting Engine explains every rupee through journals and ledger entries, the Inventory Engine must explain every single unit of stock through Inventory Movements and the Inventory Ledger.

This is the defining principle of the AaramBooks Inventory Engine.
