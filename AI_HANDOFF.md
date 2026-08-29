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

**Status:** R-7 BUSINESS EXECUTION IMPLEMENTATION COMPLETE

**What was just completed:**
1. Implemented the R-7 Architecture Audit by establishing `R7ExecutionService` and the R-7 Capability Registry pattern (`IR7Capability`).
2. Implemented the 7 authoritative R-7 action capabilities (Goods Receipt, Purchase Return, Transformation, Job Work Issue, Job Work Return, Exception Resolution, Stock Adjustment) mapped directly to their respective domain service endpoints.
3. Implemented full dependency injection integration in `ContextContainer` and `DomainsContainer` crossing boundaries for Services like `GoodsReceiptService` requiring Accounting integration.
4. Created `test_r7_execution.py` enforcing programmatic capability exhaustion verification matching the exact R-7 Census requirements.
5. Successfully tested R-7 Orchestrator intent filtering (`ACTION` only), capability ambiguity detection, and R-5 fallback delegation to UUID identifiers.
6. Generated the `docs/06-api-contracts/R-7-IMPLEMENTATION-REPORT.md` artifact.

**Current Blocker:**
- None.

**Next Steps:**
- R-7 Business Execution is complete and certified. 
- Awaiting instructions for the next phase (likely concrete data transformation adapters in AaramBrain to populate the detailed schemas for full capability execution).
