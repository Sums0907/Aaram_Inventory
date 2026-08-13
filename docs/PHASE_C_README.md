# AaramBooks Inventory Engine
# Phase C — Product UI & Operationalization

## 1. PURPOSE

Phase C converts the already-certified AaramBooks Inventory Engine into a
usable business application.

The objective is NOT to redesign the Inventory Engine.

The objective is to expose the existing backend capabilities through a
clean, simple, production-quality React UI.

The backend remains the authoritative source of:

- Inventory calculations
- Inventory movements
- Inventory balances
- BOM calculations
- Transformation calculations
- Job Worker pending stock
- Validation
- Transaction handling
- Inventory Truth
- Certification logic

The frontend is a presentation and interaction layer.

---

# 2. PHASE C STARTING CONDITION

Phase C may begin only after the following are confirmed PASS:

- Inventory Truth certification
- Daily Inventory Update certification
- BOM / Transformation certification
- Job Work Issue
- Job Work Receipt
- Job Work Return
- Multiple Receipts
- Partial Receipts
- Historical Transformation Integrity
- Decimal precision
- Transaction atomicity
- Session lifecycle / connection management

The recent session lifecycle remediation is considered complete only when:

- managed AsyncSession lifecycle is used
- persistent writes survive a fresh database session
- rollback tests pass
- Inventory → Accounting rollback passes
- Accounting → Inventory rollback passes
- NullPool / connection leak warnings are eliminated
- CLI resources are explicitly shut down

Do NOT reopen or redesign these areas as part of Phase C unless a
demonstrated regression is discovered.

---

# 3. CORE PRINCIPLE

## Backend = Truth

## Frontend = View + User Interaction

The frontend MUST NOT independently calculate:

- inventory balances
- BOM consumption
- raw material consumption
- Job Worker pending stock
- accounting amounts
- transformation quantities
- Inventory Confidence

The frontend may display calculations returned by the backend.

If a preview calculation is required for UX, the backend remains authoritative.

Example:

```text
User enters:

Received = 40 Bedsheets

        ↓

Frontend sends request

        ↓

Backend calculates:

Fabric = 115.000 m
Thread = ...
Elastic = ...
Packaging = ...

        ↓

Frontend displays result
```

The frontend must not become a second Inventory Engine.

---

# 4. PHASE C OBJECTIVE

Create a modern web interface through which the owner can understand and
operate the Inventory Engine without using the terminal.

The user should be able to answer:

1. What inventory do I have?
2. Where is it?
3. What is with Job Workers?
4. What came in today?
5. What went out?
6. What was consumed?
7. What was returned?
8. What finished goods were received?
9. Why did inventory change?
10. Is Inventory Truth healthy?
11. Are there exceptions requiring attention?

---

# 5. UI PRODUCT PHILOSOPHY

AaramBooks should NOT look like traditional accounting or ERP software.

The interface should feel:

* modern
* clean
* calm
* simple
* professional
* information-rich without being crowded

Design inspiration may include:

* Stripe
* Linear
* Vercel
* Notion

Do not copy their UI.

Use their principles:

* clear hierarchy
* generous spacing
* excellent typography
* simple navigation
* meaningful status indicators
* predictable interactions

---

# 6. TECHNOLOGY

Use the existing approved frontend stack.

```text
React
TypeScript
Vite
React Router
TanStack Query
Axios
TailwindCSS
shadcn/ui
React Hook Form
Zod
Lucide React
Recharts
```

Do not introduce another frontend framework.

Do not replace the approved stack.

---

# 7. APPLICATION STRUCTURE

The primary navigation should be organized around the actual business,
not around backend technical modules.

Recommended:

```text
Dashboard

Inventory

Job Work

Purchases

Reports

Imports

Settings
```

Accounting may appear later as an integrated module.

Do not expose technical concepts such as:

```text
InventoryMovementRepository
TransformationEngine
ServiceContainer
AsyncSession
```

to normal users.

---

# 8. DASHBOARD

The Dashboard is the operational home page.

It should answer:

> "What is happening with my inventory right now?"

Display high-value information only.

Example:

```text
TODAY

Inventory In       +XXX
Inventory Out      -XXX
Job Work Pending   XXX
Finished Goods     XXX
Exceptions         X
```

Also show:

### Inventory Health

```text
Inventory Truth
        ✓ Healthy
```

or:

```text
Inventory Truth
        ⚠ Attention Required
```

The dashboard must use backend data.

Do not calculate independent inventory balances in React.

---

# 9. INVENTORY PAGE

The Inventory page is the primary inventory workspace.

It should provide:

* Inventory Items
* SKU
* Product
* Warehouse
* Quantity
* UOM
* Available quantity
* Pending / custody quantity where applicable
* Inventory confidence/status

The user should be able to:

* search
* filter
* sort
* open an item
* view its movement history

---

# 10. INVENTORY ITEM DETAIL

Selecting an inventory item should show:

```text
PRODUCT

Current Balance

Warehouse

UOM
```

Then:

## Movement History

Example:

```text
13 Aug

PURCHASE_RECEIPT      +100

14 Aug

JOB_WORK_ISSUE         -50

15 Aug

JOB_WORK_RETURN        +10

16 Aug

JOB_WORK_RECEIPT       +20
```

The movement ledger should be treated as the explanation for the balance.

The UI must NOT invent movements.

---

# 11. INVENTORY TRUTH

Inventory Truth is a core AaramBooks concept.

The UI should make it visible.

For an inventory item:

```text
Opening Balance
      +
IN Movements
      -
OUT Movements
      =
Closing Balance
```

The UI should show a clear status:

```text
✓ VERIFIED
```

or:

```text
⚠ EXCEPTION
```

If the backend reports an inconsistency, the UI should show the exception.

Do not hide discrepancies.

---

# 12. JOB WORK WORKSPACE

Job Work should be a first-class operational workflow.

Recommended navigation:

```text
Job Work

├── Pending Stock
├── Issue Material
├── Receive Finished Goods
├── Return Material
└── Activity
```

---

# 13. JOB WORKER PENDING STOCK

Show each Job Worker's current custody position.

Example:

```text
JOB WORKER: ABC Factory

Fabric
Issued       500 m
Consumed     287.5 m
Returned      50 m
Pending      162.5 m
```

The displayed pending amount must come from the backend.

The UI must never maintain its own pending-stock calculation.

---

# 14. ISSUE MATERIAL

Provide a simple form:

```text
Job Worker
Inventory Item
Warehouse
Quantity
UOM
Reference
```

Before submitting, show a clear confirmation.

After success:

```text
Material Issued ✓
```

The backend creates the authoritative inventory movement.

---

# 15. RECEIVE FINISHED GOODS

The UI should support:

```text
Job Worker
Finished Good
Quantity
UOM
Reference
```

The backend determines:

* BOM
* Raw material consumption
* Transformation
* Finished goods movement
* Pending stock changes

The frontend only submits the business event.

Example:

```text
Receive:

100 Blue Bay Bedsheets

Backend returns:

Fabric consumed: 287.500 m
Thread consumed: ...
Elastic consumed: ...
Packaging consumed: ...
```

The UI may display the result.

---

# 16. RETURN MATERIAL

The UI must support the existing:

`JOB_WORK_RETURN`

workflow.

Example:

```text
Job Worker
Material
Return Quantity
UOM
Reference
```

Display current pending quantity before submission.

If return quantity exceeds pending:

```text
Cannot return more material
than the Job Worker's pending quantity.
```

The backend remains authoritative for validation.

---

# 17. MULTIPLE RECEIPTS

The UI must treat every physical receipt as an independent event.

Example:

```text
Receipt 1
40 Bedsheets

Receipt 2
35 Bedsheets

Receipt 3
25 Bedsheets
```

Do not create a fake "Production Order" merely to group these receipts.

Each receipt remains an independent inventory transaction.

---

# 18. PARTIAL RECEIPTS

The UI must support partial physical receipts.

Example:

Expected:

```text
100 Bedsheets
```

Received:

```text
40 Bedsheets
```

The UI should simply record:

```text
Actual Receipt = 40
```

Do not introduce Production Orders or manufacturing planning concepts merely
to represent the remaining 60.

Future physical receipts are independent transactions.

---

# 19. HISTORICAL INTEGRITY

The UI must treat historical transformations as immutable.

Example:

Historical BOM:

```text
1 Bedsheet = 2.875 m
```

Receipt:

```text
100 Bedsheets
```

Historical consumption:

```text
287.500 m
```

If the BOM later changes to:

```text
1 Bedsheet = 3.000 m
```

the old transformation must continue to display:

```text
287.500 m
```

The UI must display the stored historical result.

It must NOT recalculate history using the current BOM.

---

# 20. ACTIVITY / AUDIT VIEW

Provide a chronological operational activity view.

Example:

```text
Today

10:15
Received 50 Bedsheets from ABC Factory

11:02
Issued 100 m Fabric to XYZ Factory

13:25
Returned 20 m Fabric from XYZ Factory

15:40
Received 30 Bedsheets from XYZ Factory
```

Every event should link to its source record where appropriate.

---

# 21. IMPORTS

The UI should provide an Imports area for supported inventory data imports.

Initially expose only functionality that already exists in the backend.

Do NOT create fake import workflows merely for UI completeness.

Each import should show:

```text
File
Date
Status
Records
Errors
```

Example:

```text
ShopDeck Order Reconciliation
13 Aug 2026

✓ Processed
47 orders
0 errors
```

---

# 22. REPORTS

Phase C should expose existing backend reporting capabilities.

Do not create a new Reporting Engine merely to support the UI.

Useful initial reports:

### Inventory Balance

```text
SKU
Warehouse
Opening
In
Out
Closing
```

### Inventory Ledger

```text
Date
Movement
Reference
Qty
Balance
```

### Job Worker Pending

```text
Job Worker
Material
Issued
Consumed
Returned
Pending
```

### Inventory Exceptions

Show only actual backend exceptions.

---

# 23. SEARCH AND FILTERING

All major list screens should support:

* search
* date filter
* warehouse filter
* SKU filter
* Job Worker filter
* status filter where appropriate

Do not build complex filtering where it has no business value.

---

# 24. FORMS

Forms must be simple.

Use:

```text
React Hook Form
Zod
```

Validate obvious user errors before sending requests.

Examples:

* quantity must be greater than zero
* required fields cannot be empty
* invalid dates rejected
* return cannot exceed displayed pending quantity

However, frontend validation is NOT a substitute for backend validation.

The backend must validate again.

---

# 25. LOADING STATES

Every API operation must have a clear loading state.

Example:

```text
Receiving Finished Goods...

[spinner]
```

Do not allow accidental duplicate submissions.

Disable the primary action while a mutation is in progress.

---

# 26. ERROR HANDLING

Never display raw stack traces.

Bad:

```text
sqlalchemy.exc.IntegrityError...
```

Good:

```text
Unable to record the receipt.

The transaction was not saved.

Please try again or contact the administrator.
```

For validation errors, explain the actual business problem.

---

# 27. SUCCESS STATES

After successful mutations, clearly confirm:

```text
✓ Material Issued
✓ Material Returned
✓ Finished Goods Received
```

Then refresh relevant data using TanStack Query.

The UI must not rely on stale cached balances after a mutation.

---

# 28. DUPLICATE SUBMISSION PROTECTION

Critical inventory operations must not accidentally execute twice.

For operations such as:

* Issue
* Return
* Receipt

the UI must prevent accidental double-click submission.

The backend must also provide the authoritative duplicate/idempotency protection.

Do not rely only on frontend button disabling.

---

# 29. RESPONSIVE DESIGN

Primary use:

Desktop / Mac browser.

The UI should still work reasonably on smaller screens.

The Android application is NOT part of this Phase C.

Do not attempt to create an Android frontend during this phase.

---

# 30. ACCESSIBILITY

Use:

* readable typography
* sufficient contrast
* keyboard navigation
* visible focus states
* semantic buttons
* meaningful labels
* accessible form errors

Do not sacrifice usability for visual effects.

---

# 31. PERFORMANCE

Use TanStack Query for:

* caching
* loading states
* mutation handling
* invalidation
* background refresh

Do not introduce unnecessary state-management frameworks.

Avoid fetching the entire inventory database when only a filtered page is needed.

Use pagination where the backend supports it.

---

# 32. API RULE

The frontend must use the existing public REST API.

Do not import backend Python modules into the frontend.

Do not access the database directly.

Do not bypass API services.

Architecture:

```text
React
  ↓
REST API
  ↓
Application Service
  ↓
Domain
  ↓
Repository
  ↓
PostgreSQL
```

---

# 33. BACKEND CHANGE RULE

Phase C is primarily a frontend phase.

Backend changes are allowed ONLY when required to:

* expose an existing capability
* correct a demonstrated API defect
* provide missing data required by an already-approved workflow

Do NOT add new business logic to the backend merely because the frontend
developer finds it convenient.

If a backend business-rule change appears necessary:

STOP and document it.

---

# 34. CERTIFICATION SAFETY

The frontend must never weaken or modify backend certification tests.

Do NOT:

* change expected values
* remove failing tests
* bypass business rules
* alter inventory calculations to make the UI pass
* introduce mock data into production workflows

UI tests must test the actual API behavior.

---

# 35. TESTING REQUIREMENTS

Phase C must include:

## Component Tests

Test:

* forms
* tables
* status badges
* dialogs
* loading states
* error states

## API Integration Tests

Verify:

```text
UI
 ↓
API
 ↓
Backend
```

for important workflows.

## End-to-End Tests

At minimum test:

### Job Work Issue

```text
Issue
↓
Pending increases
↓
Primary inventory decreases
```

### Job Work Receipt

```text
Receipt
↓
Transformation
↓
Raw material consumption
↓
Finished goods increase
↓
Pending decreases
```

### Job Work Return

```text
Return
↓
Primary inventory increases
↓
Pending decreases
```

### Multiple Receipt

```text
Receipt 1
↓
Receipt 2
↓
Receipt 3
↓
Correct cumulative inventory
```

### Atomic Failure

Force a downstream failure.

Expected:

```text
No partial inventory state
```

---

# 36. FRESH DATABASE VERIFICATION

For critical UI workflows, successful API responses are NOT sufficient.

The test must verify durable persistence.

Example:

```text
UI Action
    ↓
API
    ↓
Commit
    ↓
Request ends
    ↓
NEW DATABASE SESSION
    ↓
Read record
    ↓
Record exists
```

This requirement exists because a successful request can still fail to persist
if transaction/session handling is incorrect.

---

# 37. ROLLBACK VERIFICATION

For critical multi-step workflows:

```text
UI
 ↓
API
 ↓
Inventory operation
 ↓
Downstream failure
 ↓
ROLLBACK
 ↓
NEW DATABASE SESSION
 ↓
No partial records
```

Test both directions where the workflow spans Inventory and Accounting.

---

# 38. UI CERTIFICATION

At the end of Phase C, verify:

```text
Inventory
        PASS

Job Work Issue
        PASS

Job Work Receipt
        PASS

Job Work Return
        PASS

Multiple Receipts
        PASS

Partial Receipt
        PASS

Historical Integrity
        PASS

Inventory Truth
        PASS

Atomicity
        PASS
```

All existing backend certification suites must remain PASS.

---

# 39. NO NEW BUSINESS DOMAINS

Phase C must NOT introduce:

* Production Planning
* Manufacturing Orders
* Work Centres
* Procurement redesign
* Accounting redesign
* Payment processing
* Settlement Engine
* AI Assistant
* Notifications
* Advanced warehouse management

These belong to later phases.

---

# 40. PHASE C IMPLEMENTATION ORDER

Do not build the entire UI in one pass.

Implement in this order:

## C1 — Frontend Foundation

* React/Vite setup
* Tailwind
* shadcn/ui
* routing
* API client
* authentication foundation
* shared components

↓

## C2 — Application Shell

* sidebar
* top bar
* navigation
* page layout
* responsive structure

↓

## C3 — Dashboard

* inventory health
* current balances
* pending Job Work
* exceptions
* recent activity

↓

## C4 — Inventory

* inventory list
* filters
* item detail
* movement ledger
* Inventory Truth

↓

## C5 — Job Work

* pending stock
* issue
* receipt
* return
* activity

↓

## C6 — Reports

* inventory ledger
* balance
* Job Worker pending
* exceptions

↓

## C7 — Imports

Only expose already-supported import workflows.

↓

## C8 — Error / Loading / Empty States

Complete application-wide UX states.

↓

## C9 — End-to-End UI Testing

Test real workflows.

↓

## C10 — Final UX Review

Review the complete application as a product.

---

# 41. PHASE C ACCEPTANCE CRITERIA

Phase C is complete only when:

### Functionality

* User can navigate the application.
* Inventory can be viewed.
* Inventory movement history can be viewed.
* Job Worker pending stock can be viewed.
* Job Work Issue works.
* Job Work Receipt works.
* Job Work Return works.
* Multiple receipts work.
* Partial receipts work.
* Reports work.
* Exceptions are visible.

### Integrity

* Frontend never calculates authoritative inventory.
* Backend remains authoritative.
* Fresh-session persistence tests pass.
* Rollback tests pass.
* Existing certification suites remain PASS.

### UX

* No raw technical errors shown.
* Loading states exist.
* Empty states exist.
* Success states exist.
* Error states exist.
* Duplicate submissions are prevented.
* Navigation is understandable without technical knowledge.

### Product Quality

A business owner should be able to open AaramBooks and understand:

> What inventory do I have?
>
> Where is it?
>
> What is with my Job Workers?
>
> What changed?
>
> Is my inventory trustworthy?

without opening a terminal.

---

# 42. FINAL RULE

DO NOT confuse UI completion with system completion.

A beautiful UI displaying incorrect inventory is a failure.

A simple UI displaying correct, explainable inventory is a success.

The priority order is:

1. Correctness
2. Data integrity
3. Business usability
4. Reliability
5. Visual polish

---

# 43. FIRST TASK

Do NOT immediately build all pages.

First:

1. Read the complete project documentation.
2. Read `AI_HANDOFF.md`.
3. Inspect the current backend APIs.
4. Identify which Inventory Engine capabilities are already exposed through REST.
5. Identify which UI capabilities can be implemented without backend changes.
6. Produce a Phase C implementation plan.
7. Do NOT modify code yet.

After the plan is reviewed and approved, begin with C1 — Frontend Foundation.
