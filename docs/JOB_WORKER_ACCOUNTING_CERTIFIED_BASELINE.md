# AaramBooks — Job Worker Accounting Module

## Master Implementation & Certification README

### Version: 1.0 — Post Rate Master Certification

---

# 1. Objective

Implement and certify a complete **Job Worker Accounting module** as a separate domain within the **Accounting module**.

The module manages the complete financial lifecycle of work performed by Job Workers:

```text
JOB WORK RECEIPT
       ↓
Applicable Active Rate
       ↓
Job Work Expense
       ↓
Job Worker Payable
       ↓
Payment
       ↓
Outstanding Payable
```

The module remains financially independent from the Inventory Stock Custody system.

---

# 2. Architectural Boundary

AaramBooks maintains two separate concepts.

## Inventory — Physical Stock Custody

```text
Issue
Consumption
Return
Pending
```

This answers: "Where is the physical fabric?"
*Managed by `InventoryMovementService` and `InventoryTransformationEngine`.*

## Accounting — Financial Obligation

```text
Active Rate Setup
Receipt triggers Expense
Payment
Outstanding Balance
```

This answers: "How much money do I owe Ashok Tailor?"
*Managed by `JobWorkerAccounting` domain (`RateService`, `ExpenseService`, `PaymentService`, `PayableService`).*

**Integration Point:** The only place where these two domains interact is during a `JOB_WORK_RECEIPT` (Finished Goods Received). The `GoodsReceiptService` orchestrates both:
1. `transformation_engine.execute_transformation()` -> Consumes raw material inventory.
2. `expense_service.create_from_receipt()` -> Creates financial obligation.
These happen in a **single database transaction** ensuring atomicity.

---

# 3. The "Active Rate Master" Pattern

To ensure determinism and prevent financial ambiguity, AaramBooks enforces a strict **Single Active Rate** rule for Job Work.

### The Rule

For any combination of:
> **Job Worker + Job Work Product**

There can be **only one Active Rate** at any given point in time.

### Rate Revision Flow

When a rate is revised (e.g., from ₹120 to ₹140):

```text
Old Rate ₹120
      ↓
ARCHIVED immediately (is_active=False)

New Rate ₹140
      ↓
ACTIVE immediately (is_active=True)
```

The database enforces this via a **Partial Unique Index**:
```sql
CREATE UNIQUE INDEX uix_active_job_work_rate 
ON jwa_job_work_rates (job_worker_id, sku_id) 
WHERE is_active = 1;
```

### Future Receipts Only

Every new Job Work Receipt must use **only the currently Active rate**. 
* `ExpenseService` does NOT pass an effective date to find a rate.
* It asks `RateService.get_applicable_rate()` which returns **only** the single active rate.
* If no active rate exists, the transaction fails with a `ValidationException`.

**Crucially**: Revising a rate only affects *future* receipts. Historical expenses are snapshotted and never change, regardless of how many times the rate is revised in the future.

---

# 4. Certification Invariants

The module is fully certified by `scripts/certify_job_worker_accounting.py`. All invariants below are guaranteed by automated tests.

## Rate Master Invariants
* **[A] First Rate Creation:** A new rate is created successfully.
* **[B] Exactly One Active Rate:** Database prevents two active rates for the same combination.
* **[C] Rate Revision:** Creating a new rate automatically archives the old rate.
* **[D] Archived Rate Excluded:** `get_applicable_rate` ignores archived rates.
* **[E] Archived Rate Immutable:** An archived rate cannot be deactivated again.
* **[M] Missing Active Rate Guard:** Receipt fails cleanly if no active rate exists.
* **[N] Rate Revision Affects Future Only:** New receipts use the new active rate.

## Expense & Integrity Invariants
* **[G/H] Automatic Expense Creation:** Receipt correctly triggers expense generation.
* **[I] Multiple Receipts:** Multiple receipts sum correctly.
* **[J] Partial Receipt:** Amount matches quantity * rate exactly.
* **[K] Multiple Products:** Different products in the same receipt are itemized correctly.
* **[L] Multiple Job Workers:** Job workers are fully isolated from each other.
* **[F] Historical Expense Preservation:** Rate revisions do not change historical expenses.
* **[V] Decimal Precision:** Monetary amounts correctly handle decimals.
* **[W/AB] Accounting Failure Atomicity:** If expense creation fails, the entire GRN and Inventory movement rolls back.

## Payments & Payables Invariants
* **[O/P] Payable Creation & Outstanding:** Outstanding = Total Expenses - Total Payments.
* **[Q] Partial Payment:** Outstanding balance correctly reflects partial payments.
* **[R] Multiple Payments:** Additional payments reduce the balance further.
* **[S] Overpayment Rejection:** Payments cannot exceed the total outstanding balance.
* **[T] Duplicate Receipt Protection:** The same GRN cannot generate duplicate expenses.
* **[U] Duplicate Payment Protection:** Payment references must be unique.
* **[AA.11] Zero Balance:** When fully paid, outstanding balance reaches precisely 0.
