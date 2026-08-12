# AaramBooks — Job Worker Accounting Module

## Final Product & Implementation README

### Objective

Create a **sub-domain within the Accounting module** to record:

1. Job Work expenses incurred against Job Workers.
2. Amounts payable to Job Workers.
3. Payments made to Job Workers.
4. Outstanding balances.
5. Automatic expense creation when a Job Work Receipt is posted.
6. Historical, auditable financial records.

This sub-domain sits at:

```text
src/domains/accounting/job_worker/
```

It is **architecturally separate from the Inventory module**.

The Inventory module remains responsible for **physical stock truth and custody**.

This sub-domain is responsible for the **financial relationship with the Job Worker**.

---

# 1. Core Architectural Position

```text
AaramBooks
│
├── Inventory
│   ├── Inventory Truth
│   ├── BOM
│   ├── Stock Custody
│   ├── Job Work Issue
│   ├── Job Work Receipt
│   └── Transformations
│
└── Accounting
    ├── Journals
    ├── Ledgers
    ├── Posting Rules
    └── Job Worker (this sub-domain)
        ├── Job Worker Rate Master
        ├── Job Work Expenses
        ├── Job Worker Payables
        ├── Payments
        └── Payable Ledger
```

The two modules may communicate through APIs/events, but neither owns the other's data.

---

# 2. What Each Module Owns

## Inventory Module

> **What physically happened to the stock?**

```text
Issue
Consumption
Return
Pending Stock
Job Work Receipt
Finished Goods Receipt
Inventory Movement
Inventory Balance
BOM Transformation
```

## Job Worker Accounting Sub-Domain

> **What financially happened between AaramBooks and the Job Worker?**

```text
Job Work Charge
Expense
Payable
Payment
Outstanding
```

---

# 3. Important Separation

A Job Worker can therefore have:

### Physical relationship (Inventory owns this)
```text
ABC Tailors

Cotton Fabric       600.00 m pending
Thread               10.00 kg pending
Elastic              80.00 m pending
```

### Financial relationship (Accounting / Job Worker sub-domain owns this)
```text
ABC Tailors

Job Work Charges       ₹25,000
Payments               ₹18,000
Outstanding             ₹7,000
```

These must never be represented as one combined ledger.

---

# 4. Job Worker Rate Master

The foundation of automatic expense creation is the **Job Worker Rate Master**.

A rate is defined for:

```text
Job Worker + Finished Good SKU
```

Example:

| Job Worker   | Finished Good       |  Rate | Basis     |
| ------------ | ------------------- | ----: | --------- |
| Ashok Tailor | 5-Piece Bedding Set |  ₹80  | Per Piece |
| Ashok Tailor | Single Bedsheet     |  ₹45  | Per Piece |
| XYZ Tailors  | 5-Piece Bedding Set |  ₹75  | Per Piece |

The rate belongs to the **Job Worker Accounting sub-domain**.

It is not part of:
* BOM
* Inventory Item Master
* Stock Custody
* Inventory Transformation

---

# 5. Why Rate is Based on Finished Product

The BOM determines material consumption.

The Rate Master determines labour charges.

These are deliberately independent.

```text
5-Piece Bedding Set
₹80 / piece
```

The BOM may contain:
```text
Fabric / Thread / Elastic / Packaging
```

The BOM consumes raw materials.
The Rate Master prices the labour.

---

# 6. Automatic Expense Creation

When the Inventory module posts a `JOB_WORK_RECEIPT`, the Accounting sub-domain:

1. Receives the event/reference: `{ job_worker_id, sku_id, quantity, receipt_id, receipt_date }`
2. Looks up the applicable rate from the Rate Master.
3. Calculates: `quantity × rate`
4. Creates a `JobWorkExpense` record.
5. The Payable balance is automatically derived from this.

The user should **not have to create a separate expense entry**.

---

# 7. Accounting Must Not Recalculate Inventory

The sub-domain must not calculate:
* BOM consumption
* fabric usage
* inventory balance
* pending stock
* finished goods quantity

It only consumes the **financial result of the Job Work Receipt**.

---

# 8. Job Work Receipt Integration Contract

```text
Inventory
    │
    │  JobWorkReceiptPosted
    │  {
    │      receipt_id,
    │      job_worker_id,
    │      finished_product_sku_id,
    │      quantity_received,
    │      receipt_date
    │  }
    ↓
Job Worker Accounting
    ↓ Find Rate
    ↓ Calculate Charge
    ↓ Create Expense
    ↓ Payable updated
```

The Job Work Receipt remains an **Inventory transaction**.

The Expense/Payable is an **Accounting transaction**.

---

# 9. Rate Snapshot — Immutability Rule

Once an expense is created, the rate used is permanently captured in the expense record.

```
Rate Master changes ₹80 → ₹85 in September.
August expenses remain at ₹8,000. They never become ₹8,500.
```

Every `JobWorkExpense` stores the rate at the time of creation:

```
job_worker_id
finished_product_id (sku_id)
quantity
rate             ← snapshot of rate at time of expense
rate_basis
amount           ← quantity × rate
source_receipt_id
expense_date
```

---

# 10. Rate Override

The system should support exceptional negotiated rates per receipt.

The UI must clearly indicate:

> ⚠ Rate differs from Job Worker Rate Master.

The user confirms. Once posted, the actual rate becomes part of the immutable expense record.

---

# 11. No Silent Rate Changes

**Never** dynamically calculate historical expenses from the current Rate Master.

```
Correct:
Rate Master → Rate Snapshot (at transaction time) → Immutable Expense

Wrong:
Expense → Current Rate Master → Recalculate
```

---

# 12. File Placement

```text
src/domains/accounting/job_worker/
│
├── models/
│   ├── job_work_rate.py       ← JobWorkRateModel
│   ├── job_work_expense.py    ← JobWorkExpenseModel
│   ├── job_worker_payment.py  ← JobWorkerPaymentModel
│   └── payable_allocation.py  ← PayableAllocationModel (FIFO)
│
├── schemas/
│   ├── job_work_rate.py       ← create / response schemas
│   ├── job_work_expense.py
│   ├── job_worker_payment.py
│   └── payable.py             ← payable ledger response schema
│
├── repositories/
│   ├── rates.py
│   ├── expenses.py
│   ├── payments.py
│   └── payable.py
│
├── services/
│   ├── rate_service.py        ← Rate lookup with effective-date logic
│   ├── expense_service.py     ← Expense creation from receipt event
│   ├── payment_service.py     ← Payment recording + FIFO allocation
│   └── payable_service.py     ← Payable ledger query
│
└── api/
    ├── rates.py               ← Rate Master CRUD
    ├── expenses.py            ← Expense list / detail
    ├── payments.py            ← Record payment
    └── payables.py            ← Payable ledger / summary
```

---

# 13. JobWorkExpense Model Fields

```text
id
job_worker_id              → FK: masters_suppliers.id
source_receipt_id          → UUID reference to GRN (Inventory side)
source_receipt_number      → GRN number string for display (e.g. "GRN-001")
finished_product_id        → FK: skus.id
quantity                   → Numeric(15, 3)
rate                       → Numeric(15, 2)   ← SNAPSHOT — never changes
rate_basis                 → Enum: PER_PIECE
amount                     → Numeric(15, 2)   ← quantity × rate
expense_date               → Date
status                     → Enum: POSTED / CANCELLED
reference                  → Auto-generated (e.g. JWE-120826-001)
notes
created_by / updated_by
created_on / updated_on
```

---

# 14. JobWorkerPayment Model Fields

```text
id
job_worker_id              → FK: masters_suppliers.id
payment_date               → Date
amount                     → Numeric(15, 2)
payment_account            → String (e.g. "Axis Bank")
reference                  → UTR / Cheque / Transaction ID
notes
created_by
created_on / updated_on
```

---

# 15. PayableAllocationModel (FIFO)

```text
id
expense_id                 → FK: job_work_expenses.id
payment_id                 → FK: job_worker_payments.id
allocated_amount           → Numeric(15, 2)
created_on
```

---

# 16. Payable Calculation

```text
Outstanding = SUM(expenses.amount) - SUM(payments.amount)
```

Derived from immutable transactions. Never stored as a mutable field.

---

# 17. Payable Ledger — UI Format

### Ashok Tailor

| Date   | Particular                     | Reference | Expense | Payment | Outstanding |
| ------ | ------------------------------ | --------- | ------: | ------: | ----------: |
| 12 Aug | Job Work Charges — Bedding Set | GRN-001   |  ₹8,000 |       — |      ₹8,000 |
| 15 Aug | Job Work Charges — Bedsheet    | GRN-004   |  ₹4,500 |       — |     ₹12,500 |
| 20 Aug | Payment                        | PAY-001   |       — |  ₹7,000 |      ₹5,500 |

Use: **Expense | Payment | Outstanding**

Do **not** use **Dr | Cr** in the primary UI.

---

# 18. Missing Rate Policy

If no rate is configured for a `(job_worker, sku)` pair:

* Do **not** silently create ₹0 expense.
* Show a warning on the GRN/Receipt page.
* Offer: `[ Configure Rate ]` or `[ Override Rate for this Receipt ]`.

---

# 19. Rate History

Rates are versioned by `effective_from` date:

| Job Worker   | Product     | Effective From | Rate |
| ------------ | ----------- | -------------- | ---: |
| Ashok Tailor | Bedding Set | 01 Aug 2026    |  ₹80 |
| Ashok Tailor | Bedding Set | 01 Sep 2026    |  ₹85 |

The system selects the rate whose `effective_from` is ≤ `receipt_date`.

Past expenses remain unchanged regardless of rate changes.

---

# 20. Payment Rules

* Partial payments are supported.
* Multiple payments per Job Worker are supported.
* Payments reduce outstanding via FIFO against the oldest unpaid expenses.
* Overpayment must be explicitly handled (reject or allow with confirmation).
* Payment must **not** create another expense.

---

# 21. Failure Handling

A Job Work Receipt must not be partially complete:

```
Inventory transaction succeeds
+
Accounting transaction succeeds
= Complete Receipt
```

Prefer a shared transactional service boundary. If the expense creation fails, the GRN must not be committed.

---

# 22. Accounting Container Integration

The `JobWorkerAccountingContainer` (or equivalent sub-container) should be wired inside the existing `AccountingContainer` in:

```
src/domains/accounting/dependency_injection.py
```

It provides:
- `rate_service`
- `expense_service`
- `payment_service`
- `payable_service`

---

# 23. Frontend Structure

```text
frontend/src/pages/job-worker-accounting/
├── JobWorkerAccountingDashboard.tsx
├── JobWorkerPayablesPage.tsx
├── JobWorkerPayableWorkspace.tsx
├── JobWorkRatesPage.tsx
└── JobWorkerPaymentsPage.tsx

frontend/src/components/job-worker-accounting/
├── JobWorkRateFormDialog.tsx
├── RecordJobWorkerPaymentDialog.tsx
├── JobWorkerPayableLedger.tsx
├── JobWorkerPayableSummary.tsx
└── JobWorkExpenseDetails.tsx
```

---

# 24. Navigation

A **separate top-level nav item** in Topbar:

```
Dashboard | Inventory | Job Worker Accounting | Accounting | ...
```

Under **Job Worker Accounting**:

```
Overview
Job Workers
Job Work Rates
Expenses
Payments
```

---

# 25. Certification Script

```text
scripts/certify_job_worker_accounting.py
```

Uses:

```text
test_cert_job_worker_accounting.db   ← disposable, never dev/prod
DATABASE_ENV=test                     ← required, script refuses otherwise
```

Certification areas:
- Rate creation and effective-date lookup
- Expense creation from receipt event (correct quantity × rate, Decimal-safe)
- Rate snapshot immutability
- Duplicate receipt guard (no duplicate expense)
- Payment: partial, multiple, FIFO allocation
- Payable aggregation: multi-expense + multi-payment = correct outstanding
- Complete chain: Receipt → Expense → Payable → Payment → Outstanding

---

# 26. Final Business Workflow

```text
                   JOB WORKER
                       │
             ┌─────────┴─────────┐
             │                   │
             ↓                   ↓
         INVENTORY          ACCOUNTING
             │                   │
      Stock Custody         Rate Master
             │                   │
        Issue/Return       Job Work Expense
             │                   │
             ↓                   ↓
       Job Work Receipt      Payable
             │                   │
             │                   ↓
             │                Payment
             │                   │
             │                   ↓
             │              Outstanding
             │
             ↓
       Transformation
             │
             ↓
      Finished Goods
```

---

# 27. Final Architectural Principle

> **Do not turn Job Worker Accounting into another feature inside Inventory. It is a sub-domain of Accounting that consumes Job Work Receipt events from Inventory and maintains its own financial truth.**

Inventory answers: **What happened to the physical stock?**

Job Worker Accounting answers: **What did the Job Worker earn, what have we paid, and what do we still owe?**

The formal Accounting module can then answer: **How does this financial activity enter the company's books?**
