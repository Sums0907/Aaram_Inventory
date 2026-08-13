# AaramBooks — Master Certification Test Standard

**Purpose:** Update the relevant AaramBooks certification/master-test README to make **end-to-end production-path testing and transaction integrity mandatory** for every future master test.

---

## 1. Core Rule

A master test must **not** certify a feature merely because its individual services pass their isolated tests.

Every important workflow must be tested through the **same top-level production service/API path used by the actual application**.

### Insufficient

```text
Test → ExpenseService
     → PASS
```

### Required

```text
Actual User Action
       ↓
Production API
       ↓
Top-Level Service
       ↓
Child Services
       ↓
Database Transaction
       ↓
COMMIT
       ↓
Fresh Database Session
       ↓
Verify Durable Result
```

The test must prove that the complete workflow works, not merely that individual components work.

---

# 2. Three-Level Certification Model

Every master test must cover three levels.

## Level 1 — Component / Business Logic

Verify:

* calculations
* validations
* business rules
* decimal precision
* status transitions
* master-data rules
* historical rules

Example:

```text
Active Rate ₹150
Receipt Quantity 10
Expected Expense ₹1,500
Actual Expense ₹1,500
```

---

## Level 2 — Production Workflow

The test must invoke the **real production orchestration path**.

For example, Job Worker Accounting must not only test:

```text
ExpenseService
RateService
PayableService
```

individually.

It must test:

```text
JOB_WORK_RECEIPT
        ↓
GoodsReceiptService
        ↓
Inventory processing
        ↓
Transformation / Consumption
        ↓
Active Rate lookup
        ↓
Job Work Expense
        ↓
Job Worker Payable
        ↓
Transaction Commit
```

The test must use the actual service/API path used by the frontend.

---

# 3. Transaction Boundary Certification

Transaction integrity is a **first-class certification requirement**.

Whenever one service calls another service, the master test must verify that the child service participates in the **same database transaction/session**.

### Example

A Goods Receipt may trigger:

```text
GoodsReceiptService
        ↓
InventoryMovementService
        ↓
TransformationEngine
        ↓
ExpenseService
        ↓
PayableService
```

All operations that belong to the same business transaction must participate in the same transaction boundary.

### Forbidden architecture

```text
GoodsReceiptService
      │
   Session A
      │
      └── ExpenseService
              │
           Session B ❌
```

This can create an expense that exists only in an uncommitted or detached session.

### Required architecture

```text
GoodsReceiptService
      │
   Session A
      │
      ├── Inventory
      ├── Transformation
      ├── Expense
      └── Payable
```

All are committed or rolled back together.

---

# 4. Durable Persistence Test

A successful operation inside the current SQLAlchemy session is **not sufficient evidence of success**.

After the workflow completes, the certification test must:

1. Complete the production workflow.
2. Commit the transaction.
3. Close the current session.
4. Open a **fresh database session**.
5. Query the database again.
6. Verify that the expected records actually exist.

### Required pattern

```text
Production Workflow
       ↓
COMMIT
       ↓
Close Session
       ↓
Open Fresh Session
       ↓
Query Database
       ↓
Verify Persistent Result
```

This specifically protects against bugs where a record was created in memory or in a parallel session but never actually committed.

---

# 5. Atomic Rollback Tests

Every multi-step financial/inventory workflow must have deliberate failure tests.

## Test A — Downstream Failure

Example:

```text
JOB_WORK_RECEIPT
      ↓
GRN created
      ↓
Inventory movement created
      ↓
Accounting Expense attempted
      ↓
FORCED ACCOUNTING FAILURE
```

Expected:

```text
GRN                 ROLLBACK
Inventory Movement  ROLLBACK
Transformation      ROLLBACK
Expense             ROLLBACK
Payable             ROLLBACK
```

There must be **no partial records**.

---

## Test B — Upstream / Final Failure

Also test the reverse direction where possible:

```text
JOB_WORK_RECEIPT
      ↓
Inventory succeeds
      ↓
Accounting succeeds
      ↓
Final operation fails
```

Expected:

```text
Everything ROLLS BACK
```

The system must never leave:

```text
Inventory exists
but Accounting missing
```

or:

```text
Accounting exists
but Inventory missing
```

unless the architecture explicitly defines that workflow as asynchronous.

---

# 6. Orphan Record Detection

Master tests must explicitly check for orphan records.

Examples:

### Inventory

```text
GRN exists
but Inventory Movement missing
```

### Accounting

```text
Job Work Expense exists
but corresponding GRN does not exist
```

### Payable

```text
Payable exists
but Expense does not exist
```

### Job Worker

```text
Consumption exists
but corresponding Job Work Issue does not exist
```

Such conditions must cause certification failure.

---

# 7. Duplicate / Idempotency Testing

Where a user action can accidentally be submitted twice, the master test must verify the expected duplicate behavior.

For example:

```text
Same GRN submitted twice
```

The test must verify that the system does not accidentally create:

```text
2 GRNs
2 Expenses
2 Payables
2 Inventory transformations
```

unless duplicate transactions are explicitly allowed by the business design.

---

# 8. Historical Integrity

Master tests must verify that subsequent master-data changes do not alter historical transactions.

Example:

```text
Rate = ₹150
       ↓
GRN
       ↓
Expense = ₹1,500
       ↓
Rate revised to ₹200
```

Expected:

```text
Old Expense remains ₹1,500
Old Rate remains historically identifiable
New ₹200 rate applies only to future work
```

Similarly, BOM changes must not rewrite historical transformations.

---

# 9. Cross-Domain Integration Testing

AaramBooks deliberately separates:

```text
INVENTORY
```

from:

```text
ACCOUNTING
```

Master tests must therefore verify **both integration and isolation**.

### Integration

Example:

```text
JOB_WORK_RECEIPT
       ↓
Inventory
       +
Accounting
```

Both sides must correctly reflect the same business event.

### Isolation

A change in Accounting must not corrupt:

* Inventory Movement
* Stock Custody
* BOM
* Transformation
* Finished Goods inventory

And Inventory changes must not bypass Accounting rules.

---

# 10. Real API / Service Path Requirement

Where a workflow is available through an API, certification should preferably invoke the API-level production path.

If the test cannot reasonably run an HTTP server, it may invoke the exact top-level production service directly.

However, it must **not bypass orchestration** by directly calling child repositories/services unless the test is specifically a unit/component test.

### Good

```text
GoodsReceiptService.create(...)
```

### Weak for integration certification

```text
ExpenseRepository.create(...)
```

The latter can be useful for a unit test but cannot certify the complete GRN → Accounting workflow.

---

# 11. Test Database Safety

Every certification script must use an isolated disposable database.

For example:

```text
test_cert_bom.db
test_cert_inventory.db
test_cert_accounting.db
test_cert_custody.db
```

### NEVER use

```text
test_manual.db
```

or:

```text
production.db
```

for destructive certification tests.

Certification scripts may perform:

```text
drop_all()
DELETE
reset
seed
```

**only against their own isolated test database.**

---

# 12. Database Environment Guard

Certification scripts must identify themselves as running in a test environment.

Example:

```text
DATABASE_ENV=test
```

Production/development databases must reject destructive test operations.

The certification suite should fail immediately if an unsafe database is detected.

---

# 13. Master Test Structure

Every future master certification suite should follow this structure:

```text
A. Environment Safety
B. Master Data
C. Component / Business Logic
D. Real Production Workflow
E. Transaction / Session Integrity
F. Commit Persistence
G. Rollback
H. Orphan Detection
I. Duplicate / Idempotency
J. Historical Integrity
K. Cross-Domain Integration
L. Cross-Domain Isolation
M. Regression Tests
```

Not every feature needs every test, but the applicable categories must be explicitly considered.

---

# 14. Example — Job Worker Accounting

The Job Worker Accounting master test must include an actual:

```text
JOB_WORK_RECEIPT
```

and verify:

```text
GRN
 ↓
Inventory Movement
 ↓
Job Work Consumption
 ↓
Active Rate
 ↓
Job Work Expense
 ↓
Job Worker Payable
 ↓
COMMIT
 ↓
Fresh DB Session
 ↓
All records verified
```

It must also test:

```text
Rate Revision
Multiple Receipts
Partial Receipts
Payment
Partial Payment
Historical Rate
Rollback
Duplicate Receipt
```

and verify that Inventory and Accounting remain correctly separated.

---

# 15. Master Test Pass Criteria

A module cannot be marked:

```text
CERTIFIED: PASS
```

merely because its mathematical/business tests pass.

Certification requires:

```text
Business Logic              PASS
Production Workflow         PASS
Transaction Boundary       PASS
Durable Persistence         PASS
Rollback                    PASS
Orphan Detection            PASS
Historical Integrity        PASS
Integration                 PASS
Isolation                   PASS
Regression                  PASS
Database Safety             PASS
```

Any critical failure results in:

```text
CERTIFICATION: FAIL
```

---

# 16. Important Lesson From Previous Failure

The previous Job Worker Accounting issue demonstrated why this standard is mandatory.

The individual Accounting logic worked:

```text
Rate lookup       PASS
Expense creation  PASS
Payable logic     PASS
```

But the real workflow failed because:

```text
GoodsReceiptService
        ↓
ExpenseService
        ↓
different session
        ↓
expense not durably committed
```

Therefore:

> **Component certification is not integration certification.**

A master test must prove the complete production workflow and its transaction boundary.

---

# 17. Permanent AaramBooks Certification Principle

Going forward, the definition of a certified feature is:

> **The feature works correctly when executed exactly as the user executes it, all participating services share the correct transaction boundary, the committed result survives a fresh database session, failures roll back the entire business transaction, and no orphan or duplicate records are produced.**

This requirement applies to **all future AaramBooks master tests**, including Inventory, Accounting, Job Worker Accounting, BOM, Stock Custody, and any future modules.
