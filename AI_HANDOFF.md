# AaramBooks — AI Handoff Protocol

## 1. Purpose

This file is the single source of truth for handing the AaramBooks project between AI coding agents.

AaramBooks may be developed by:

- Gemini — Primary Coding Agent
- Claude Sonnet — Backup Coding Agent
- Claude Opus — Review / Senior Reasoning Agent

ChatGPT is used separately by the human owner for:

- Business interpretation
- Accounting logic
- Architecture
- Requirements
- Product decisions

This file allows Gemini and Claude to continue the project without requiring the human owner to manually explain what the previous AI did.

---

## 1.1 PATH OF AI_HANDOFF.md

This file lives at the **root** of the AaramBooks project directory:

```
/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/AI_HANDOFF.md
```

---

# 2. CRITICAL RULE

Every AI coding agent MUST read this file before making changes.

Every AI coding agent MUST inspect the actual current project before making changes.

The AI_HANDOFF.md file describes the expected state, but the actual files in the repository are the ultimate source of truth.

If this file conflicts with the actual code:

1. Do not guess.
2. Inspect the code.
3. Identify the discrepancy.
4. Explain it.
5. Preserve the working implementation unless a change is explicitly required.

---

## 2.1 DATABASE WRITE TESTING RULE (PERMANENT)

For every feature that creates, updates, or deletes persistent data, the AI must explicitly test and verify the following:

1. Test that the API/request succeeds.
2. Test that the database contains the expected result using a **fresh database session**.
3. Test the resulting business calculation/state.
4. Test the UI/API response where applicable.
5. For important financial transactions, verify that the data survives session/request completion.

**A successful HTTP response or in-memory SQLAlchemy success must never be considered sufficient proof that a database write worked.**

---

# 3. AI ROLES

## ChatGPT — Architecture / Interpretation

ChatGPT is primarily responsible for helping the human owner with:

- Business requirements
- Accounting interpretation
- GST logic
- Inventory logic
- Architecture
- Feature definition
- Reviewing proposed approaches
- Explaining technical concepts in simple English

ChatGPT is NOT the default coding agent.

---

## Gemini — PRIMARY CODING AGENT

Gemini is the primary implementation agent.

When Gemini is available:

- Gemini should normally perform coding tasks.
- Gemini should preserve the established architecture.
- Gemini should implement approved requirements.
- Gemini should run appropriate tests.
- Gemini should update this file after meaningful work.

Gemini must NOT unnecessarily rewrite working code created by another AI.

If Claude previously implemented something successfully, Gemini should first understand it before changing it.

---

## Claude Sonnet — BACKUP CODING AGENT

Claude Sonnet is the backup implementation agent.

Claude Sonnet is used primarily when:

- Gemini's usage limit is exhausted.
- Gemini is temporarily unavailable.
- The human owner explicitly asks Claude to implement a task.

Claude Sonnet must:

- Read this file first.
- Inspect the current project.
- Continue from the current state.
- Preserve the existing architecture.
- Avoid unnecessary refactoring.
- Avoid redesigning modules merely because Claude would design them differently.
- Run appropriate tests.
- Update this file before completing the task.

Claude Sonnet should behave as a temporary replacement for Gemini, NOT as a new architect.

---

## Claude Opus — REVIEW / SENIOR REASONING

Claude Opus is primarily a reviewer.

Use Opus for:

- Complex architectural questions
- Large refactor reviews
- Difficult bugs
- Cross-module problems
- Accounting logic review
- Finding hidden edge cases
- Reviewing whether implementation matches the intended architecture

Opus should not modify working code unless explicitly instructed.

---

# 4. MODEL SWITCHING PROTOCOL

## Gemini → Claude

When Gemini becomes unavailable or its usage limit is exhausted:

Claude must assume that Gemini was the primary developer.

Claude should:

1. Read this file.
2. Inspect the current Git status.
3. Inspect the current project structure.
4. Identify the last completed task.
5. Inspect the files changed in that task.
6. Continue from the current implementation.
7. Do NOT redesign the architecture.
8. Complete only the required task.
9. Run tests.
10. Update this file.

The human owner should NOT have to manually explain the handoff.

---

## Claude → Gemini

When Gemini becomes available again:

Gemini should:

1. Read this file.
2. Inspect the current Git status.
3. Inspect the files changed since Gemini's previous session.
4. Understand what Claude implemented.
5. Verify the implementation against the existing architecture.
6. Continue from the current state.
7. Do NOT automatically rewrite Claude's work.
8. Preserve working code unless there is a demonstrated problem.
9. Run appropriate tests.
10. Update this file.

Again, the human owner should NOT have to manually explain the handoff.

---

# 5. DO NOT CREATE AI-TO-AI ARCHITECTURAL DRIFT

Gemini and Claude may have different programming preferences.

They may disagree about:

- Class structure
- Function structure
- Naming
- File organization
- Design patterns
- Abstractions
- Error handling

This does NOT automatically mean the existing implementation should be changed.

The established AaramBooks architecture takes priority over an individual AI's preferred coding style.

Do NOT repeatedly rewrite:

Gemini → Claude → Gemini → Claude

unless there is a genuine technical reason.

---

# 6. BEFORE STARTING A TASK

The AI must:

### Step 1 — Read this file

Understand:

- Current project state
- Previous AI's work
- Known issues
- Current task
- Next steps

### Step 2 — Inspect the repository

Check:

- Project structure
- Git status
- Relevant files
- Tests
- Recent changes

### Step 3 — Understand before modifying

Do not immediately start editing files.

First understand how the relevant part of the existing system works.

---

# 7. TASK SCOPE

Only modify files relevant to the current task.

Do NOT:

- Refactor unrelated modules.
- Rename unrelated files.
- Change established architecture.
- Change accounting treatment without approval.
- Change database structure unnecessarily.
- Remove existing functionality.
- Replace working code simply because a different implementation looks cleaner.

If a larger architectural change appears necessary:

STOP and explain:

1. What problem was discovered?
2. Why the current architecture is insufficient?
3. What change is proposed?
4. Which modules would be affected?
5. What risks exist?

Do not silently perform the larger redesign.

---

# 8. ACCOUNTING LOGIC RULE

AaramBooks is an accounting system.

Accounting behaviour is more important than code elegance.

Never change accounting treatment merely because a different implementation is technically simpler.

Important areas include:

- Sales
- Sales returns
- Credit notes
- Payment gateway settlements
- Receivables
- Expenses
- Purchases
- GST
- Inventory
- Journal entries
- Ledgers
- Financial statements

If accounting treatment is unclear:

STOP.

Do not guess.

The human owner will clarify the accounting decision, usually with ChatGPT.

---

# 9. AARAMBOOKS ARCHITECTURAL VISION

AaramBooks is intended to become an accounting automation engine rather than simply a traditional accounting application.

General flow:

```
Business Data
        ↓
Data Validation
        ↓
Standardized Business Events
        ↓
Accounting Rules
        ↓
Journal Entries
        ↓
Ledger
        ↓
Reports / Financial Statements
```

The architecture should keep these responsibilities reasonably separated:

- Data ingestion
- Data normalization
- Business logic
- Accounting logic
- Reporting
- Export

---

# 10. VERSION 1 REFERENCE

AaramBooks Accounting Version 1 is the behavioural reference implementation for existing accounting logic.

Version 1 should be treated as a source of truth for existing behaviour unless the human owner explicitly approves a change.

The goal of future versions is:

```
Version 1
    ↓
Understand existing behaviour
    ↓
Preserve accounting logic
    ↓
Improve architecture
    ↓
Add functionality
```

Do NOT assume that a rewrite is an opportunity to invent new accounting behaviour.

---

# 11. INVENTORY VISION

The long-term AaramBooks inventory direction is an Inventory Truth Engine.

Inventory should ultimately be explainable through immutable Inventory Movements.

Examples include:

- Purchase / Receipt
- Issue
- Consumption
- Return
- Adjustment
- Transfer

Inventory Balance should be derived from inventory movements rather than maintained as an unexplained number.

Inventory Confidence is an important long-term KPI.

---

# 12. JOB WORKER INVENTORY

AaramBooks may track inventory held by job workers.

Important concepts:

```
Issue
    ↓
Consumption
    ↓
Return
    ↓
Pending
```

The Stock Custody Ledger should be a derived operational view.

It should not become a second independent source of inventory truth.

Existing inventory models and terminology should be inspected before creating new ones.

---

# 13. E-COMMERCE CONTEXT

Aaram Homes is the business context for AaramBooks.

Relevant systems include:

- ShopDeck
- Razorpay
- Shipping / courier systems
- Bank accounts
- GST
- Inventory

ShopDeck provides order / sales information.

Payment gateways may collect customer payments and subsequently settle funds into the bank.

Therefore payment gateway receivables may be required.

Example:

```
Customer
    ↓
Payment Gateway
    ↓
Payment Gateway Receivable
    ↓
Settlement
    ↓
Bank
```

Do not assume that ShopDeck is a receivable merely because ShopDeck manages orders.

Determine which entity actually owes the money.

---

# 14. PURCHASES WITHOUT TAX INVOICE

Goods may be received before a supplier issues the tax invoice.

Distinguish between:

- Physical receipt of goods
- Purchase recognition
- Supplier invoice
- GST input tax credit

Do not claim GST merely because goods were physically received.

If GRNI / unbilled purchase accounting is introduced, it must be deliberately designed and tested.

---

# 15. CURRENT PROJECT STATE

## Current Primary Coding Agent

Antigravity

## Previous Coding Agent

Gemini

## Current Feature

Packer ↔ Inventory Integration Certification Suite v1.0

## Status

**ALL PASS**

## Validated Inventory Responsibilities

- **CERT-001**: Inventory successfully consumes PACKED events and creates SALES_FULFILLMENT movements.
- **CERT-002**: Webhook idempotency verified (duplicate events return ALREADY_PROCESSED safely).
- **CERT-003**: Forward fulfillment recovery (downstream outage handled through Packer outbox retry; eventual delivery creates exactly one inventory movement).
- **CERT-004**: RTO_RECEIVED events process correctly (creates RTO_RETURN, restores inventory, rejects duplicates).
- **CERT-005**: Partial RTO handling validated.
- **CERT-006**: RTO event delivery recovery validated during Inventory downtime.
- **CERT-007**: Cancellation before fulfillment validated (no unintended stock mutation).

## Important Architecture Clarification

Inventory does NOT interpret return conditions such as GOOD/DAMAGED.
**Packer owns**: return reconciliation, item condition decision, filtering of non-restockable items.
**Inventory owns**: receiving inventory-eligible events, ledger mutation, stock truth, idempotent processing.

## Current Certified Contract
Packer sends valid inventory mutation events. Inventory processes them exactly once.
Future changes must preserve: webhook contract, event_id idempotency, inventory ledger integrity, movement immutability, duplicate event handling. Do not introduce condition/disposition logic into Inventory unless a deliberate future feature phase is started.

## Files Changed

- `src/domains/operations/models/sales_order.py`
- `src/domains/operations/schemas/lifecycle.py`
- `src/domains/operations/services/lifecycle_engine.py`
- `src/domains/operations/services/reconciliation_orchestrator.py`
- `src/domains/data_ingestion/services/adapters/shopdeck_order.py`
- `src/app/services/pipeline_orchestrator.py`
- `src/domains/connectors/services/shopdeck.py`
- `frontend/src/pages/inventory/DailyUpdatePage.tsx`
- `tests/operations/test_phase_d_inventory.py`
- `tests/operations/test_reconciliation_orchestrator.py`

## Tests Run

- `PYTHONPATH=. venv/bin/pytest tests/operations tests/inventory_truth -v` (33/33 PASS)
- `PYTHONPATH=. venv/bin/python scripts/certify_inventory_truth.py` (Exit Code 0)

## Test Result

**PASS**

## Known Issues

- Pre-existing SQLAlchemy `NullPool` connection warnings during tests. Noted as technical debt.

## Important Decisions

- **Phase D Architecture**: 
  - Physical Inventory is the only inventory tracked.
  - PACK and EXPIRED AWB logic infers missing boundaries based strictly on cumulative sum of previous immutable movements per SKU.
  - No `select(WarehouseModel).limit(1)` is used; instead we rely on explicit configuration `SHOPDECK_SALES_WAREHOUSE_CODE`.

## Next Exact Step

**Phase D** is complete and certified. Wait for the human owner to provide instructions for the next phase or confirm the infrastructure hardening task.



---

# 16. HANDOFF LOG

### 2026-08-14 — Gemini (Phase D Complete Certification & Testing)

Task: Expand Phase D test matrix and complete certification.
Changes:
- Verified CUSTOMER_RETURN logic relies solely on `return_delivered_date` and is completely independent of the `RETURNED` order status. Updated test case to test customer returns from `DELIVERED` status.
- Implemented `test_inventory_movement_failure_rollback` to verify strict transactional atomicity during Phase D inventory generation.
- Added comprehensive tests for RTO, customer returns, neutral statuses, multi-SKU, and idempotency to `test_phase_d_inventory.py`.
- Fixed `MissingGreenlet` lazy-loading bug by pre-initializing the new order items list.
- Fixed flaky tests caused by `datetime.utcnow()` mismatches by propagating `observed_at` down to the transition models.
- Enforced `SHOPDECK_SALES_WAREHOUSE_CODE` checks without defaults.
- Tests: `pytest tests/operations tests/inventory_truth -v` passed (34/34).
- Certification: `certify_inventory_truth.py` passed with exit code 0.
Status: Complete
Next step: Wait for the human owner to approve the Phase D implementation and provide instructions for the next phase or Infrastructure Hardening.

---

### 2026-08-12 — Gemini (Job Worker Accounting Frontend)

Task: Implement Job Worker Accounting Frontend UI

Changes:
- Created `frontend/src/api/job-worker-accounting.ts` with React Query hooks.
- Refactored `AccountingPage.tsx` into an `AccountingLayout.tsx` which includes the new `Job Worker Accounting` sub-navigation.
- Implemented `JobWorkerAccountingDashboard.tsx` for high-level KPIs and outstanding balances.
- Implemented `JobWorkerPayablesWorkspace.tsx` for chronological worker ledger view and statement downloading.
- Implemented `JobWorkRatesPage.tsx` and `JobWorkRateFormDialog.tsx` for rate configuration.
- Verified TypeScript build and routes.
- Fully adhered to the separation of concerns: Job Worker Accounting is inside Accounting, separate from Inventory.

Files:
- `frontend/src/App.tsx`
- `frontend/src/api/job-worker-accounting.ts`
- `frontend/src/components/layout/AccountingLayout.tsx`
- `frontend/src/pages/AccountingDashboardPage.tsx` (renamed from `AccountingPage.tsx`)
- `frontend/src/pages/accounting/job-worker-accounting/*`
- `frontend/src/components/job-worker-accounting/*`

Tests: `npm run build` and Smoke Tests — PASS

Status: Complete (Frontend)

Next step: Wait for the human owner to provide instructions for the next feature.

---

### 2026-08-12 — Gemini (Job Worker Accounting Backend)

Task: Implement Job Worker Accounting Backend Domain

Changes:
- Created Job Worker Accounting sub-domain inside `src/domains/accounting/job_worker/`
- Implemented `JobWorkRateModel`, `JobWorkExpenseModel`, `JobWorkerPaymentModel`, `PayableAllocationModel`
- Implemented Repositories and Services (`RateService`, `ExpenseService`, `PaymentService`, `PayableService`)
- Added FIFO allocation logic for payments
- Integrated `ExpenseService.create_from_receipt` into `GoodsReceiptService` for automatic expense creation
- Registered 4 new API routers (`rates`, `expenses`, `payments`, `payables`)
- Wired DI container and updated `app/container.py` and `app/main.py`
- Created `scripts/certify_job_worker_accounting.py` (16/16 tests passing)

Files:
- `src/domains/accounting/job_worker/` (New sub-domain)
- `src/domains/accounting/dependency_injection.py`
- `src/app/container.py`, `src/app/main.py`
- `src/domains/inventory/services/goods_receipt.py`
- `scripts/certify_job_worker_accounting.py`

Tests: `certify_job_worker_accounting.py` — 16/16 PASS

Status: Complete (Backend)

Next step: Implement Frontend UI (Dashboard, Payables Page, Rates Page, Dialogs)

---

### 2026-08-12 — Gemini (earlier session)

Task: Database Safety Protocol + Inventory Certification baseline

Changes:
- Implemented 3-tier DB environment (dev/test/prod isolation)
- Restored Ashok Tailor and Terracotta Bloom Bedsheet manual data
- Created golden backups
- Passed all 4 original certification suites

Files: `src/foundation/database/`, `scripts/certify_*.py`, `docs/INVENTORY_CERTIFIED_BASELINE.md`, `.agents/AGENTS.md`

Tests: certify_bom_module, certify_inventory_truth, certify_daily_inventory_update, certify_job_worker_allocation — all PASS

Status: Complete

Next step: Implement Stock Custody Ledger

---

### 2026-08-12 — Claude Sonnet

Task: Stock Custody Ledger implementation

Changes:
- Added 3 new Pydantic schemas: `StockCustodyLedgerEntry`, `StockCustodyLedgerItemSummary`, `StockCustodyLedgerResponse`
- Added `get_stock_custody_ledger()` to `JobWorkRepository`
- Added `get_custody_ledger()` to `JobWorkService`
- Added `GET /inventory/job-works/suppliers/{supplier_id}/custody-ledger` API endpoint
- Created `scripts/certify_stock_custody_ledger.py` with 13 tests (A–M)

Files:
- `src/domains/inventory/schemas/job_work.py`
- `src/domains/inventory/repositories/job_work.py`
- `src/domains/inventory/services/job_work.py`
- `src/domains/inventory/api/job_work.py`
- `scripts/certify_stock_custody_ledger.py`
- `reports/stock_custody_ledger_report.md`

Tests: All 5 certification suites — PASS (13/13 new tests + 4 regression suites)

Status: Complete

Next step: UI page for Stock Custody, or Job Worker Accounting — pending human owner decision

---

# 17. COMPLETION PROTOCOL

Before declaring a task complete, the AI MUST:

1. Run appropriate tests.
2. Check for obvious errors.
3. Review the files changed.
4. Confirm existing functionality has not been unnecessarily altered.
5. Update the CURRENT PROJECT STATE section.
6. Add a short entry to the HANDOFF LOG.
7. Clearly state:
   - What changed
   - Why it changed
   - Files changed
   - Tests performed
   - Known issues
   - Next step

---

# 18. GIT SAFETY

Before a large or risky change, create a Git checkpoint whenever practical.

Do not reset, delete, or overwrite previous work without explicit approval.

Never use destructive Git commands merely to solve a coding problem.

Examples of potentially destructive commands that require caution:

- git reset --hard
- git clean -fd
- deleting large groups of files
- force pushing

The project's history is part of the safety mechanism.

---

# 19. COMMUNICATION STYLE

The human owner is not expected to understand every line of Python.

After completing a task, explain the result in simple English.

Use this structure:

### What changed

Explain the feature in plain English.

### Why

Explain the business / technical reason.

### What files changed

List them.

### What was tested

Explain the tests.

### What could go wrong

Mention relevant risks.

### What happens next

Give the next logical step.

Do not overwhelm the owner with unnecessary implementation details unless requested.

---

# 20. HUMAN DECISION RULE

The AI is the implementer.

The human owner is the final decision maker for:

- Business rules
- Accounting treatment
- Product behaviour
- Major architecture
- Data interpretation
- Scope

If a requirement is ambiguous and the ambiguity could materially affect the system:

STOP.

Explain the alternatives.

Do not silently choose a business or accounting rule.

---

# 21. GOLDEN RULE

READ.

UNDERSTAND.

PRESERVE.

IMPLEMENT.

---

### 2026-08-17 — Antigravity (Integration Certification Suite v1.0)

Task: Record Packer ↔ Inventory Integration Certification results.
Changes:
- Documented ALL PASS status for CERT-001 through CERT-007.
- Clarified the architectural boundary: Packer is responsible for return condition filtering, while Inventory remains a strict ledger for eligible stock.
- Codified the certified webhook contract regarding idempotency and immutability.
Status: Complete
Next step: Await next human owner instruction.

TEST.

UPDATE THIS FILE.

The next AI should be able to open the project and continue the work without the human owner having to explain what happened previously.
