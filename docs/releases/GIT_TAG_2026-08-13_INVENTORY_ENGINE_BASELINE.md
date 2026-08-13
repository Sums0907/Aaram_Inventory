# AaramBooks Inventory Engine
# Git Tag Baseline — 13 August 2026

**Date:** 13 August 2026  
**Domain:** Inventory Engine  
**Purpose:** Historical Git checkpoint / architectural baseline  
**Status:** Certified Core + Operational UI Foundation  
**Next Major Work:** ShopDeck Order Lifecycle & Dynamic Rolling Window

---

# 1. Purpose of This Git Tag

This Git tag represents the state of the AaramBooks Inventory Engine immediately before the next major architectural enhancement:

> ShopDeck Order Lifecycle Synchronization and Dynamic Rolling Report Window.

This document is a historical record of what has actually been achieved at this point.

It is NOT a future roadmap.

It must not claim functionality as complete merely because it has been designed.

Only functionality that was implemented, tested, or explicitly certified before this checkpoint should be described as completed.

---

# 2. The Original Business Problem

The Inventory Engine was created to solve one fundamental business problem:

> Maintain true inventory while taking into account ShopDeck orders, cancellations, RTOs, returns, purchases, and Job Work.

The system was not intended to be a conventional inventory-management application where users manually edit stock quantities.

The fundamental requirement was:

> For every SKU/item, AaramBooks should be able to explain why the current inventory balance is what it is.

---

# 3. Core Inventory Philosophy

AaramBooks Inventory is designed as an:

# Inventory Truth Engine

The system does not treat the current stock number as the source of truth.

Instead:

```text
Business Event
      ↓
Inventory Movement
      ↓
Inventory Ledger
      ↓
Inventory Balance
      ↓
Inventory Exceptions
      ↓
Inventory Confidence
```

The Inventory Balance is derived from Inventory Movements.

Users should not directly edit the inventory balance.

---

# 4. Inventory Truth Model

The fundamental invariant is:

```text
Opening Stock
+
All Positive Inventory Movements
-
All Negative Inventory Movements
=
Current Inventory Balance
```

Every movement must have an explainable business origin.

Examples:

```text
OPENING_STOCK
PURCHASE_RECEIPT
SALE
JOB_WORK_ISSUE
JOB_WORK_RETURN
RAW_MATERIAL_CONSUMPTION
TRANSFORMATION
```

The exact movement types are owned by the Inventory Engine.

---

# 5. Immutable Inventory Ledger

The Inventory Ledger is the authoritative historical record of inventory movements.

It is intended to answer:

> What happened to this inventory?

For example:

```text
Opening Stock             +100
Purchase Receipt           +50
Sale                        -8
Job Work Issue             -20
Job Work Return             +5
Raw Material Consumption   -10
```

The resulting balance is derived from those movements.

The system therefore does not depend on a manually maintained stock field.

---

# 6. Inventory Confidence

Inventory Confidence was established as a first-class concept.

It is not merely a dashboard decoration.

The objective is to communicate how trustworthy the calculated inventory position is.

The broader design treats:

```text
Inventory Balance
+
Inventory Exceptions
+
Inventory Confidence
```

as related aspects of Inventory Truth.

---

# 7. Inventory Exceptions

The system is designed to surface situations requiring attention rather than silently hiding them.

Examples include:

* Negative stock
* Missing BOM
* Missing UOM
* Pending Job Work
* Other inventory integrity exceptions

The Phase 3 Inventory Intelligence Dashboard was designed around surfacing these operational exceptions.

---

# 8. Goods Receipt Workflow

The inbound inventory workflow was implemented as a Goods Receipt Note (GRN).

The implemented design includes:

* Human-readable GRN identifiers
* POSTED GRNs for the current pilot workflow
* Goods Receipt Register
* Supplier information
* Warehouse information
* Invoice information
* SKU count
* Units
* Status
* Read-only GRN detail
* Inventory impact visibility
* Product Workspace → Receive Goods quick action
* GRN reference attached to the resulting inventory movement

Example:

```text
Supplier Delivery
      ↓
Goods Receipt Note
      ↓
PURCHASE_RECEIPT
      ↓
Inventory Movement
      ↓
Inventory Balance
```

The GRN workflow therefore operates through the Inventory Truth Engine rather than directly changing stock. 

---

# 9. Daily Inventory Update

The Daily Inventory Update workflow was implemented around the ShopDeck Order Reconciliation Report.

At this checkpoint, the system already supports the concept of:

```text
ShopDeck Order Report
       ↓
Daily Inventory Update
       ↓
Inventory Movements
       ↓
Inventory Truth
```

The existing certification suite for Daily Inventory Update is part of the certified regression baseline. 

---

# 10. Important Limitation Identified After the Initial Implementation

The existing Daily Inventory Update model has now exposed an important real-world limitation.

ShopDeck's Order Reconciliation Report is a mutable snapshot.

An order created on one date may change status much later.

Example:

```text
10 Aug
Order created / delivered

19 Aug
Order becomes RTO
```

The changed RTO status may appear in a later report while retaining the original Order Date.

Therefore:

> A report for a particular date cannot safely be interpreted as a list of inventory events that occurred on that date.

This is the next major architectural enhancement.

The current Git tag records this limitation explicitly rather than pretending that the existing Daily Inventory Update completely solves late status changes.

---

# 11. Job Work — Certified Inventory Foundation

Job Work was implemented as an Inventory transformation/custody workflow.

The core physical lifecycle is:

```text
Raw Material
     ↓
Job Work Issue
     ↓
Job Worker Custody
     ↓
Job Work Receipt
     ↓
BOM-based Consumption
     ↓
Finished Goods
```

---

# 12. Job Worker Custody Model

The Job Worker custody model is deliberately simple.

AaramBooks tracks:

```text
Issue
Consumption
Return
Pending
```

The fundamental calculation is:

```text
Pending
=
Issued
-
Consumption
-
Return
```

This is a derived custody view over the existing Inventory movement/allocation records. 

---

# 13. What Job Worker Inventory Means

At this checkpoint, Job Worker inventory means:

> **Raw material issued to the Job Worker that has not yet been accounted for through recorded consumption or return.**

AaramBooks does NOT attempt to estimate:

* Finished Goods physically sitting at the Job Worker
* WIP at the Job Worker
* Production completed but not reported
* Finished Goods "ready for pickup"
* Internal Job Worker production inventory

These concepts are deliberately outside the current Inventory Truth boundary.

The system records what AaramBooks can establish through business events.

---

# 14. Job Work Receipt

When Finished Goods are actually received from a Job Worker:

```text
JOB_WORK_RECEIPT
       ↓
Finished Goods increase
       +
BOM-based raw-material consumption
       ↓
Job Worker pending raw material decreases
```

The BOM therefore determines the material consumption associated with the Finished Goods actually received.

It is NOT used to estimate how many Finished Goods the Job Worker currently possesses.

---

# 15. BOM / Transformation Engine

The BOM and Transformation Engine was implemented and certified for the current scope.

The certified scope includes:

* Decimal precision
* Raw-material consumption
* Job Worker pending stock
* Atomicity
* Purchased Finished Goods isolation
* Inventory Truth
* Job Work Return
* Over-pending Return protection
* Multiple Receipts
* Partial Receipts
* Multiple + Partial Receipts
* Historical Transformation Integrity
* BOM change does not alter historical consumption
* Inventory Truth after multiple receipts and returns

The branch documentation records the Inventory Transformation Engine + BOM + Job Work workflow as having completed its current certification scope. 

---

# 16. Decimal Precision

Inventory quantities are treated as exact quantities.

The engine uses Decimal/Numeric-style precision rather than floating-point arithmetic for inventory calculations.

Example:

```text
BOM:
2.875 m / Finished Unit

Receipt:
100 units

Consumption:
287.5 m
```

The engine must preserve the exact mathematical quantity.

The UI may format the value as:

```text
287.50 m
```

without changing the underlying quantity.

---

# 17. FIFO Job Worker Allocation

Job Worker material consumption supports FIFO allocation against outstanding Issue References.

Example:

```text
Issue 1 = 280 m
Issue 2 = 250 m

Consumption = 287.50 m
```

Allocation:

```text
Issue 1 → 280.00 m
Issue 2 →   7.50 m
```

This provides traceability without requiring artificial physical batch numbers.

---

# 18. Job Work Returns

Job Work Return was implemented and certified.

A valid return:

```text
Job Worker Pending
        ↓
decreases
        +
Warehouse/Primary Inventory
        ↓
increases
```

Over-return attempts must fail atomically.

No partial inventory mutation is permitted.

---

# 19. Multiple and Partial Job Work Receipts

The transformation engine supports:

* Multiple receipts
* Partial receipts
* Multiple + partial receipts

Historical transformation records remain protected from later changes to the BOM.

This is important because historical inventory truth must describe what actually happened at the time of the transaction.

---

# 20. Stock Custody Ledger

The Stock Custody Ledger has been implemented and certified.

Its purpose is to answer:

> What raw material has been entrusted to a Job Worker, what has been consumed, what has been returned, and what remains pending?

The ledger terminology is intentionally:

```text
Issue
Consumption
Return
Pending
```

It does not use accounting terminology such as:

```text
Dr
Cr
Debit
Credit
```

---

# 21. Stock Custody Ledger Certification

The Stock Custody Ledger certification contains 13 tests.

The branch records:

```text
Stock Custody Ledger        13/13 PASS
BOM Certification           PASS
Job Worker Allocation       PASS
Inventory Truth             PASS
Daily Inventory Update      PASS
```

The Stock Custody Ledger certification covered:

* Basic Issue
* Consumption
* Return
* Lifecycle
* Multiple Issues
* FIFO Consumption
* Decimal Precision
* Over-Return Validation
* Historical Integrity
* Finished Goods Isolation
* All Items View

The ledger is a read-only derived view and does not create a second Inventory Truth Engine. 

---

# 22. Stock Custody API

The certified Stock Custody Ledger exposes:

```text
GET /inventory/job-works/suppliers/{supplier_id}/custody-ledger
```

with optional item filtering:

```text
?item_id=<SKU_ID>
```

The API preserves:

* Per-item separation
* UOM separation
* Decimal precision
* Finished Goods isolation
* Existing FIFO allocation
* Existing Inventory Truth

---

# 23. Finished Goods Isolation

Purchased Finished Goods are deliberately isolated from Job Worker custody.

Finished Goods must not automatically appear in the Job Worker Stock Custody Ledger merely because they exist in the Inventory Item Master.

The Stock Custody Ledger is fundamentally about material entrusted to Job Workers.

---

# 24. Job Worker Accounting — Architectural Decision

Job Worker Accounting was separated from Inventory.

The architecture is:

```text
AaramBooks
│
├── Inventory
│   ├── Inventory Truth
│   ├── BOM
│   ├── Job Work
│   ├── Stock Custody
│   └── Transformations
│
└── Accounting
    └── Job Worker Accounting
```

Inventory answers:

> What happened to physical material?

Accounting answers:

> How much money is owed to the Job Worker?

The two domains must not maintain each other's balances.

---

# 25. Integration Boundary

The Job Work Receipt is the integration point.

Conceptually:

```text
                 JOB WORK RECEIPT
                        │
              ┌─────────┴─────────┐
              ↓                   ↓
         INVENTORY             ACCOUNTING
              │                   │
       Material Flow         Labour Expense
              │                   │
       Stock Custody         Job Worker Payable
                                  │
                               Payment
                                  │
                              Outstanding
```

The Inventory module owns physical stock.

The Accounting module owns the financial relationship.

---

# 26. Job Worker Rate Master

The Job Worker Rate Master has now been implemented and certified.

The certified architecture enforces:

> Exactly one Active Rate per Job Worker + Job Worked Product.

Creating a new rate:

```text
Old Rate
   ↓
ARCHIVED

New Rate
   ↓
ACTIVE
```

The revision is atomic.

---

# 27. Rate Master Database Protection

A database-level partial unique index was implemented to prevent more than one active rate for the same:

```text
Job Worker + Product
```

The application layer also enforces the same rule.

This means the invariant is protected both by:

```text
Application Logic
```

and:

```text
Database Constraint
```

This is a particularly important integrity achievement.

---

# 28. Historical Rate Protection

If a Job Worker rate changes:

```text
₹120
```

to:

```text
₹140
```

the old rate becomes:

```text
ARCHIVED
```

but remains historically valid.

An expense previously calculated at:

```text
20 × ₹120 = ₹2,400
```

must remain ₹2,400.

It must never be recalculated at ₹140.

The Rate Master therefore controls future transactions while historical accounting transactions preserve what actually happened. 

---

# 29. Archived Rate Protection

Archived rates:

* Cannot be used for future transactions.
* Cannot be casually edited.
* Cannot be reactivated through the normal workflow.
* Cannot be deactivated/deleted if already historically used.

The rate revision mechanism is the approved method for changing the current rate.

---

# 30. Job Worker Accounting Status at This Checkpoint

IMPORTANT:

The **Rate Master is certified**.

The **complete Job Worker Accounting lifecycle is NOT yet claimed as fully certified by this Git tag** unless its master end-to-end certification has independently passed.

The planned complete lifecycle is:

```text
Job Work Receipt
      ↓
Rate Lookup
      ↓
Expense
      ↓
Payable
      ↓
Payment
      ↓
Outstanding
```

The complete Job Worker Accounting master certification remains a separate milestone.

---

# 31. Database Safety

Database safety was explicitly addressed.

The certification architecture separates:

```text
Development Database
```

from:

```text
Disposable Certification Databases
```

The documented baseline records:

```text
test_manual.db
```

as the protected development/manual database.

Certification suites use separate databases such as:

```text
test_cert_*.db
```

Golden backups were also established outside the project directory.

The certification record states:

```text
Database Safety            PASS
Database Isolation         PASS
Development DB Protection  PASS
```

This protection is part of the Inventory baseline and must not be weakened by future work. 

---

# 32. Certification Baseline

The consolidated Inventory certification baseline includes:

```text
BOM Module                  PASS
Inventory Truth             PASS
Daily Inventory Update      PASS
Job Worker Allocation       PASS
Stock Custody Ledger        13/13 PASS
Database Safety             PASS
Database Isolation          PASS
Mathematical Precision      PASS
Transaction Atomicity       PASS
Historical Integrity        PASS
Job Work Return             PASS
Multiple Receipts           PASS
Partial Receipts            PASS
FIFO Allocation             PASS
```

The branch documentation explicitly records the overall Inventory certification as:

```text
OVERALL CERTIFICATION: PASS
```

for the certified scope. 

---

# 33. Inventory UI / Operational Foundation

The Inventory UI has progressed beyond a pure backend engine.

The implemented operational direction includes:

* Inventory Dashboard
* Inventory Items
* Product/Item Workspace
* Job Worker Workspace
* Goods Receipt
* Activity Register
* Transformation Register
* Daily Inventory Update workflow

The dashboard was deliberately redesigned as an:

> Inventory Intelligence Control Centre

rather than a folder/tree-style database interface.

Its intended operational questions are:

```text
What inventory do I have?
What needs attention?
What happened recently?
What is with Job Workers?
What is low?
What is negative?
What receipts happened?
Has today's update been completed?
```

The Phase 3 implementation order was defined as:

```text
3A Dashboard
3B Inventory Items
3C Item Workspace
3D Job Worker Workspace
3E GRN UX
3F Activity Register
3G Transformation Register
3H Error Handling / UX
3I Full Regression
```

Phase 3 is therefore an operationalization layer over the certified engine, not a replacement for it. 

---

# 34. UI Architectural Principle

The UI must not duplicate Inventory business logic.

The preferred flow is:

```text
User Action
    ↓
Existing Business Service
    ↓
Inventory Movement
    ↓
Inventory Truth Engine
```

Phase 3 should primarily:

> Read → display → trigger existing certified transactions.

It should not:

> Recalculate → duplicate → replace the Inventory Truth Engine.

This is an explicit architectural freeze rule. 

---

# 35. Central UOM Direction

A central Unit of Measure Master was established as the intended architecture for the expanding Inventory domain.

The central UOM should be used for:

* Raw Materials
* Consumables
* Packaging
* Semi-Finished Goods
* Future inventory categories
* BOM components

The existing 67 Finished Goods SKUs were deliberately protected from unnecessary UOM restructuring.

The principle is:

> Create a UOM once and reuse the same UOM everywhere.

---

# 36. Existing 67 Finished Goods

The existing 67 Finished Goods SKUs are protected.

Future master-data expansion must not unnecessarily migrate, rebuild, or corrupt these existing records.

This is an explicit regression requirement.

---

# 37. Inventory Master Data Architecture

The broader Inventory Master architecture established during development includes:

```text
Inventory Classification
Inventory Item
SKU
Supplier
Job Worker
Warehouse
Unit of Measure
Brand
Collection
Attributes
```

The principle is:

> Master data defines what exists. Transactions define what happened.

The certified Inventory engine should reference master data rather than duplicating business identities inside transactions.

---

# 38. No Barcode Workflow at This Baseline

Barcode scanning is deliberately outside the current pilot scope.

Current inventory operations use:

* Item/SKU selection
* Manual quantity entry
* UOM-aware quantities

Barcode functionality remains future scope.

---

# 39. No Multi-Warehouse Operational Workflow at This Baseline

The current business operates with one primary warehouse.

The current Phase 3 scope therefore does not introduce complex warehouse transfer workflows.

Future multi-warehouse support remains possible without changing the fundamental Inventory Truth model.

---

# 40. What Is Proven at This Git Tag

The following can be treated as established/certified for the documented scope:

### Inventory Truth

* Immutable Inventory Movements
* Derived Inventory Balance
* Inventory Ledger
* Inventory Confidence
* Inventory Exceptions

### Inbound

* Goods Receipt / GRN
* Purchase Receipt movement
* GRN traceability

### Job Work

* Job Work Issue
* Job Worker Pending Material
* Job Work Receipt
* BOM-based Consumption
* Job Work Return
* Multiple Receipts
* Partial Receipts
* Historical Transformation Integrity
* FIFO allocation
* Stock Custody Ledger

### Quantity Integrity

* Decimal precision
* UOM-aware quantity handling
* No floating-point inventory arithmetic

### Safety

* Certification DB isolation
* Development DB protection
* Golden backup strategy
* Atomic transactions
* Regression certification

### Accounting Boundary

* Job Worker Accounting separated from Inventory
* Job Worker Rate Master implemented
* Active/Archived rate architecture certified

---

# 41. What Is NOT Yet Claimed as Complete

The following must NOT be represented as completed merely because architecture/design exists.

## ShopDeck Late Status Synchronization

Not yet implemented as the final dynamic state-reconciliation architecture.

## Dynamic Rolling Window

Not yet implemented.

## Administrative Inventory for RTO / Returns

The business requirement has now been defined but is part of the next implementation.

## Complete Job Worker Accounting

Rate Master is certified, but the complete:

```text
Receipt → Expense → Payable → Payment → Outstanding
```

master lifecycle requires its own certification.

## Full Production Pilot

The existence of certified automated tests does not equal complete production validation.

## Live ShopDeck Connector

The current workflow remains manual report download/upload.

The live ShopDeck connector is not the dependency for the next implementation.

---

# 42. Critical Architectural Freeze

From this Git tag onward, the following certified Inventory logic must be treated as frozen.

Do not modify without a documented defect or explicit architectural change:

* Inventory Movement mathematics
* Inventory Balance calculation
* Inventory Truth calculation
* BOM mathematical calculation
* Transformation calculation
* Job Worker Pending calculation
* FIFO allocation
* Transaction boundaries
* Historical transformation logic
* Stock Custody Ledger calculation

If modification becomes necessary:

1. Document the reason.
2. Make the smallest possible change.
3. Add/modify certification tests.
4. Run all existing certification suites.
5. Confirm no regression.
6. Update this baseline documentation.

---

# 43. Current Architectural Boundary

The Inventory architecture at this checkpoint is:

```text
                         INVENTORY
                             │
                 ┌───────────┴───────────┐
                 │                       │
          INVENTORY TRUTH           JOB WORK
                 │                       │
        Inventory Movements       Issue / Receipt / Return
                 │                       │
        Inventory Ledger          Job Worker Custody
                 │                       │
        Inventory Balance          Stock Custody Ledger
                 │                       │
        Inventory Confidence             BOM
                                         │
                                  Transformation
```

Accounting remains separate:

```text
                         ACCOUNTING
                             │
                     JOB WORKER A/C
                             │
                    Rate Master
                    Expense
                    Payable
                    Payment
                    Outstanding
```

The integration point is the Job Work Receipt.

---

# 44. Why This Git Tag Matters

This is not merely a code snapshot.

It marks the point at which the project moved from:

> "Can we build the Inventory Engine?"

to:

> "We have a certified Inventory Truth foundation and can now build operational workflows on top of it."

The core mathematical and transactional foundation is no longer the experimental part of the project.

Future work should therefore be incremental and controlled.

---

# 45. Immediate Next Architectural Problem

The next major problem to solve is ShopDeck order lifecycle reconciliation.

The business reality is:

```text
ShopDeck Order
      ↓
Status can change later
      ↓
Historical report row can change
      ↓
Daily report does not necessarily represent
today's inventory event
```

The next architecture must therefore support:

```text
Manual ShopDeck Report Upload
        ↓
External Order State
        ↓
State History
        ↓
State Transition Detection
        ↓
Inventory Event
```

The next implementation must also support:

### Active Orders

```text
PRINT
PACK
IN-TRANSIT
HANDOVER
RTO_ACKNOWLEDGED
RTO_INITIATED
DELIVERED
```

with:

```text
DELIVERED
=
Active until Customer Return Window expires
```

### Terminal Orders

```text
RTO_DELIVERED
RETURNED
CANCELLED INITIATED
```

subject to the final lifecycle mapping.

---

# 46. Customer Return Policy

Current business policy:

```text
Customer Return Window = 7 days
```

This must NOT be hardcoded.

It must be:

* Configurable
* Effective-dated
* Preserved historically for orders governed by an earlier policy

Example:

```text
Policy A
13-Aug-2026
7 days

Policy B
01-Oct-2026
10 days
```

An order delivered under Policy A remains governed by 7 days.

---

# 47. Dynamic Rolling Window — Next Design

The next report window must NOT be an arbitrary:

```text
60 days
```

The target logic is:

```text
Oldest Active Inventory Order Date
                ↓
Report Start Date

Today
                ↓
Report End Date
```

The report range therefore follows the actual unresolved inventory lifecycle.

A configurable safety buffer may be added later.

---

# 48. Mandatory Out-of-Window Safety

If AaramBooks asks the user to download:

```text
10-Aug → 19-Aug
```

and the uploaded report contains:

```text
08-Aug Order
```

that record must NOT modify inventory during this import.

It must be classified as:

```text
OUT_OF_WINDOW
```

and shown to the user for reconciliation.

It must not silently create an Inventory Movement.

This is a mandatory safety boundary for the next implementation.

---

# 49. Initialisation Principle for the Next Phase

Initial inventory setup must remain separate from historical ShopDeck state.

The initialisation workflow will eventually be:

```text
Physical Stock Count
        ↓
OPENING_STOCK
```

separately:

```text
ShopDeck Historical Report
        ↓
External Order State Baseline
```

Historical ShopDeck orders must not simply be replayed as historical Inventory Movements during initialisation.

This prevents a historical report from corrupting the actual physical opening stock.

---

# 50. Administrative vs Physical Inventory — Next Phase

The next ShopDeck lifecycle design will distinguish:

## Physical Inventory

Stock physically in AaramBooks' possession.

## Administrative Inventory

Inventory expected to return but not yet physically received.

Example:

```text
RTO_INITIATED
      ↓
Administrative Inventory +1
```

Then:

```text
RTO_DELIVERED
      ↓
Administrative Inventory -1
Physical Inventory +1
```

The same principle applies to customer returns.

Administrative inventory must not be treated as physically available stock.

---

# 51. Job Work Scope Going Forward

Job Worker Finished Goods/WIP tracking is explicitly OUT OF SCOPE.

The Inventory module will continue to maintain only:

> **Raw Material Pending with Job Worker**

calculated as:

```text
Issued
-
Recorded Consumption
-
Recorded Return
=
Pending
```

When a Job Work Receipt occurs:

```text
Finished Goods +
Raw Material Consumption -
Job Worker Pending -
```

No additional "pickup" or "ready for pickup" concept should be introduced.

---

# 52. Git Tag Interpretation

This tag should be treated as:

> **AaramBooks Inventory Engine — Certified Foundation / Pre-ShopDeck-Lifecycle Enhancement**

It is NOT:

```text
Final Production Release
```

It is NOT:

```text
Complete Inventory Product
```

It IS:

```text
Stable Architectural Baseline
+
Certified Inventory Truth Foundation
+
Certified Job Work Foundation
+
Operational UI Foundation
```

---

# 53. Suggested Git Tag

Recommended tag:

```text
inventory-v1.0.0-beta.20260813
```

or, if the repository already uses simpler release tags:

```text
v1.0.0-beta.20260813
```

The tag should point to the exact commit represented by this document.

---

# 54. Git Tag Procedure

Before creating the tag:

```bash
git status
```

Confirm the intended working tree state.

Then:

```bash
git add .
git commit -m "chore: establish inventory engine certified baseline"
```

Verify:

```bash
git log -1 --oneline
git status
```

Create the annotated tag:

```bash
git tag -a inventory-v1.0.0-beta.20260813 \
  -m "AaramBooks Inventory Engine certified baseline - 13 Aug 2026"
```

Verify:

```bash
git tag -n
git show inventory-v1.0.0-beta.20260813
```

If the repository uses a remote:

```bash
git push origin <commit>
git push origin inventory-v1.0.0-beta.20260813
```

Do not force-update or move this tag later.

If the baseline needs correction, create a new tag.

---

# 55. Golden Baseline Principle

This Git tag represents the code baseline.

The certification databases/backups represent the corresponding data baseline.

Both should be preserved.

```text
Git Tag
   +
Certified Code
   +
Certification Scripts
   +
Protected Development DB
   +
Golden Backup
   =
Inventory Baseline
```

Future changes must be measurable against this baseline.

---

# 56. Final Statement

As of 13 August 2026, AaramBooks has moved substantially beyond a prototype Inventory database.

The system has a certified Inventory Truth foundation in which:

```text
Business Events
      ↓
Inventory Movements
      ↓
Inventory Ledger
      ↓
Inventory Balance
```

is the authoritative inventory architecture.

The Job Work engine can explain:

```text
Issue
Consumption
Return
Pending
```

and the Stock Custody Ledger has been independently certified.

The BOM/Transformation engine has been certified for decimal precision, atomicity, returns, multiple/partial receipts and historical integrity.

The Goods Receipt workflow provides the inbound operational path.

The Job Worker Rate Master has a protected Active/Archived architecture.

The operational UI has moved toward an Inventory Intelligence Control Centre.

The next major work is therefore not to redesign the Inventory Truth Engine.

It is to solve the remaining real-world synchronization problem:

> **How does AaramBooks reliably convert manually uploaded, mutable ShopDeck order states into correct inventory events without missing late RTOs/returns or corrupting inventory?**

That problem is intentionally left for the next development phase.

---

# END OF BASELINE
