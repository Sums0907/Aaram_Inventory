# Job Worker Rate Master — Strict Active/Archived Architecture

## Objective

Implement a strict Rate Master for Job Worker Accounting.

For every:

> **Job Worker + Job Worked Product**

there must be **exactly one Active Rate**.

When a new rate is created:

```text
Existing Active Rate
        ↓
     ARCHIVED
        ↓
New Rate
        ↓
      ACTIVE
```

This must happen **atomically**.

Archived rates are historical records and must never be used for future Job Work Accounting transactions.

---

## 1. Core Invariants

### Invariant 1 — One Active Rate

For every:

```text
(job_worker_id, sku_id)
```

the database must contain:

```text
exactly 0 or 1 Active Rate
```

Normally there should be one once a rate has been configured.

It must never be possible to have:

```text
Ashok Tailor + Bedding Set
₹120 ACTIVE
₹140 ACTIVE
```

simultaneously.

---

### Invariant 2 — Rate Revision Archives the Previous Rate

When ₹120 is active:

```text
₹120 → ACTIVE
```

and the user creates ₹140:

```text
₹120 → ARCHIVED
₹140 → ACTIVE
```

This must occur in a **single database transaction**.

---

### Invariant 3 — Archived Rates Cannot Be Used

All future Job Work Expense calculations must resolve the rate using:

```text
job_worker_id
+
sku_id
+
is_active = TRUE
```

An archived rate must never be returned as the applicable rate.

---

### Invariant 4 — Archived Rates Are Immutable

Once:

```text
is_active = FALSE
```

the rate must be read-only.

No:

* Edit
* Delete
* Reactivate
* Reuse

through the normal application UI/API.

---

### Invariant 5 — Historical Expenses Preserve Their Rate

If an old transaction used:

```text
₹120
```

and the rate is later revised to:

```text
₹140
```

the historical expense remains:

```text
Rate Used = ₹120
```

It must never be recalculated using ₹140.

The Job Work Expense should retain:

```text
rate_version_id
rate_used
quantity
expense_amount
```

or the equivalent fields already established by the Accounting domain.

---

# 2. Effective Date

`effective_from` should **remain in the Rate Master**.

It is historical information and should not be removed merely because `is_active` controls future lookup.

Example:

| Rate | Effective From | Status   |
| ---: | -------------- | -------- |
| ₹100 | 01-Jun-2026    | Archived |
| ₹120 | 01-Aug-2026    | Archived |
| ₹140 | 13-Aug-2026    | Active   |

The current active rate is ₹140.

`effective_from` tells us **when that version was introduced**.

---

# 3. Rate Creation / Revision

Do not implement revision as:

```text
DELETE old rate
CREATE new rate
```

Instead:

```text
BEGIN TRANSACTION

Find active rate
        ↓
Archive active rate
        ↓
Create new rate
        ↓
COMMIT
```

If any step fails:

```text
ROLLBACK
```

The old active rate must remain active.

---

# 4. Database-Level Protection

Do not rely only on Python/service logic to enforce one active rate.
A partial unique index is implemented at the database level:

```sql
CREATE UNIQUE INDEX idx_jwa_rates_single_active 
ON jwa_job_work_rates (job_worker_id, sku_id) 
WHERE is_active = 1;
```

This ensures two layers of protection: Application validation + Database constraint.

---

# 5. Final Invariant

The system should guarantee:

> **For every Job Worker + Job Worked Product combination, there can be at most one Active Rate. Creating a revised rate atomically archives the previous active rate and makes the new rate the only active rate. Archived rates are immutable and can never be used for future transactions. Historical Job Work Expenses permanently retain the rate version and rate actually used at the time of recognition.**

---

# 6. Implementation Summary

## 6.1 Database Constraints
- Created an Alembic migration (`85bbd97c3bd7`) and manually applied a SQLite **partial unique index** (`idx_jwa_rates_single_active`) to `jwa_job_work_rates`.
- This enforces at the database level that there can never be more than one rate where `is_active = 1` for the same Job Worker + Product.

## 6.2 Backend Logic Enforcement
- Updated `JobWorkRateRepository.get_applicable_rate()` to strictly filter by `is_active == True`. It no longer falls back or looks at `effective_from` dates to determine the active rate.
- Updated `RateService.create_rate()` to perform an **atomic revision**: it archives the current active rate and creates the new one in a single transaction. If the transaction rolls back, the old rate remains active.
- Added usage validation to `RateService.deactivate_rate()`. The service now checks the `JobWorkExpenseRepository` and **rejects** deactivation if a rate has been historically used.

## 6.3 Frontend Clarity
- Updated the `JobWorkerRates.tsx` screen to properly label inactive rates as **Archived**.
- Changed the "Add Rate" modal to explicitly state:
  > **Note:** If an active rate already exists for this combination, it will be automatically archived, and this new rate will become the only active rate.
- The submit button was changed to "Revise / Create Rate".

## 6.4 Certification
- Created `scripts/certify_job_worker_rates.py` which executes and proves all 11 test cases (A through M). The certification suite fully passes and verifies:
  A. First Rate
  B. Rate Revision (Old Archived, New Active)
  C. Single Active Rate (Database constraint)
  D. Active Rate Lookup
  E. Archived Rate Exclusion
  F. Historical Expense Preservation
  G/H. Archived Rate Modification Guard
  I. Used Rate Deletion Guard
  J. Atomic Revision
  K. No Active Rate Fallback
  L. Different Product Isolation
  M. Different Job Worker Isolation
