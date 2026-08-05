# Accounting Engine

## Purpose

The Accounting Engine is responsible for translating business events into financial transactions.

It consumes validated business documents from upstream domains such as Operations, Matching, and Inventory, and generates canonical accounting entries that accurately represent the financial impact of each business event.

The Accounting Engine is the single source of truth for all accounting transactions within AaramBooks.

It does not import data, perform document matching, or manage inventory.

Its sole responsibility is to convert business activity into accounting records using deterministic posting rules.

---

# Position in System Architecture

```text id="jzwfrs"
External Platforms
        │
        ▼
Data Ingestion
        │
        ▼
Operations Domain
        │
        ▼
Matching Domain
        │
        ▼
Inventory Engine
        │
        ▼
========================
  Accounting Engine
========================
        │
        ├────────► Vyapar Export
        ├────────► Financial Reports
        └────────► Future ERP Integrations
```

---

# Responsibilities

The Accounting Engine is responsible for:

* Generating Journal Entries.
* Applying accounting posting rules.
* Managing Ledgers.
* Posting debit and credit transactions.
* Recording inventory valuation impacts.
* Recording receivables and payables.
* Recording payment gateway charges.
* Recording logistics expenses.
* Recording settlement adjustments.
* Producing Trial Balance data.

The Accounting Engine is **not** responsible for:

* Importing files.
* Parsing CSV reports.
* Matching business documents.
* Managing inventory.
* Maintaining customer or supplier masters.
* Exporting data to external accounting software.

---

# Core Principles

The Accounting Engine follows six fundamental principles.

## 1. Event Driven

Every accounting entry originates from a business event.

Examples:

* Sale
* Customer Return
* Payment Received
* Settlement Received
* Stock Adjustment
* Inventory Valuation
* Refund

---

## 2. Double Entry Accounting

Every Journal Entry must balance.

```text id="drntbl"
Total Debit

=

Total Credit
```

No Journal Entry may be posted unless balanced.

---

## 3. Immutable Accounting

Posted Journal Entries cannot be edited.

Corrections must be recorded using reversing or adjustment entries.

---

## 4. Deterministic Posting

The same business event must always generate the same accounting result under the same posting rules.

There is no ambiguity in journal generation.

---

## 5. Auditability

Every Journal Entry must be traceable back to its originating business document.

Examples:

* Sales Order
* Tax Invoice
* Settlement
* Payment
* Inventory Movement

---

## 6. Separation of Concerns

Business logic belongs to upstream domains.

The Accounting Engine only interprets approved business events and converts them into accounting transactions.

---

# Business Objects

## Journal Entry

Represents one accounting transaction.

Contains one or more Journal Lines.

---

## Journal Line

Represents one debit or credit posting within a Journal Entry.

Every Journal Entry must contain at least two Journal Lines.

---

## Ledger

Represents an accounting account.

Examples:

* Sales
* Accounts Receivable
* Inventory Asset
* Cost of Goods Sold
* GST Output
* GST Input
* Shipping Expense
* Payment Gateway Charges
* COD Charges
* Bank

---

## Account Mapping

Defines which Ledger should be used for each business event.

Example:

```text id="ejk9zm"
SALE

↓

Sales Ledger

GST Output Ledger

Accounts Receivable Ledger
```

---

## Posting Rule

Defines how accounting entries are generated from business events.

Posting Rules are deterministic and configurable.

---

## Financial Period

Represents an accounting period used for posting and reporting.

Only open financial periods may accept new Journal Entries.

---

## Trial Balance

Represents the summarized balances of all Ledgers.

It is derived entirely from posted Journal Entries.

---

# Accounting Workflow

```text id="ukekxo"
Business Event
      │
      ▼
Posting Rule
      │
      ▼
Ledger Mapping
      │
      ▼
Journal Entry
      │
      ▼
Journal Lines
      │
      ▼
Trial Balance
      │
      ▼
Financial Reports
      │
      ▼
Vyapar Export
```

---

# Business Events

Examples of events that produce accounting entries:

* Sales Order Completed
* Tax Invoice Posted
* Customer Return Processed
* Payment Received
* Settlement Received
* Refund Issued
* Inventory Adjustment
* Inventory Valuation
* Write-off

---

# Reports

The Accounting Engine supports:

* Journal Register
* General Ledger
* Trial Balance
* Profit & Loss Statement
* Balance Sheet
* GST Reports
* Expense Analysis
* Revenue Analysis

---

# Events

The Accounting Engine publishes:

* JournalEntryCreated
* JournalPosted
* JournalReversed
* FinancialPeriodClosed
* TrialBalanceUpdated

Future integrations may subscribe to these events.

---

# Design Principles

The Accounting Engine must always be:

* Deterministic
* Balanced
* Auditable
* Immutable
* Event Driven
* Idempotent

Accounting transactions must never be entered manually when they originate from automated business events.

Every accounting entry must be traceable back to the originating business document.

---

# Future Roadmap

## Version 1

* Ledgers
* Journal Entries
* Journal Lines
* Posting Rules
* Account Mapping
* Trial Balance

## Version 2

* Profit & Loss
* Balance Sheet
* GST Reports
* Financial Period Closing

## Version 3

* Multi-company Accounting
* Multi-currency
* Budgeting
* Cost Centers

## Version 4

* Consolidated Financial Statements
* Branch Accounting
* Advanced Tax Rules

## Version 5

* AI-assisted Journal Validation
* Financial Anomaly Detection
* Predictive Financial Analytics

---

# Guiding Principle

**Every financial transaction must originate from a verified business event.**

The Accounting Engine never invents accounting entries.

It faithfully converts approved business events into deterministic, balanced, and fully auditable Journal Entries that become the foundation for financial reporting and external accounting system exports.
