# Accounting Business Objects

## Purpose

This directory contains the detailed functional specifications for every Business Object within the Accounting Engine.

While `docs/accounting/README.md` defines the architecture, responsibilities, and guiding principles of the Accounting Engine, the documents in this folder define the behavior, lifecycle, validation rules, and relationships of each individual Business Object.

Each Business Object specification serves as the authoritative reference for implementation.

Developers, architects, AI coding agents, and testers should consult these specifications before implementing or modifying any accounting functionality.

---

# Business Objects

## 01. Ledger

Represents an accounting account used for financial recording.

Examples include:

* Sales
* Accounts Receivable
* Accounts Payable
* Inventory Asset
* Cost of Goods Sold
* GST Input
* GST Output
* Bank
* Cash
* Shipping Expense
* Payment Gateway Charges

Ledgers classify financial transactions and form the foundation of the accounting system.

---

## 02. Journal Entry

Represents one complete accounting transaction.

Every Journal Entry contains one or more Journal Lines and must always remain balanced.

Journal Entries are immutable once posted.

---

## 03. Journal Line

Represents an individual debit or credit posting within a Journal Entry.

Every Journal Entry must contain at least two Journal Lines.

Journal Lines determine how business events affect individual Ledgers.

---

## 04. Account Mapping

Defines which Ledger should be used for specific business events.

Examples:

* Sale
* Customer Return
* Settlement
* Payment Gateway Charges
* Shipping Charges
* Inventory Adjustment

Account Mapping separates accounting configuration from business logic.

---

## 05. Posting Rule

Defines how accounting entries are generated from business events.

Posting Rules translate Operations, Matching, and Inventory events into balanced Journal Entries.

---

## 06. Financial Period

Represents an accounting period for transaction posting and financial reporting.

Financial Periods control when Journal Entries may be posted and support financial closing procedures.

---

## 07. Trial Balance

Represents the summarized balances of all Ledgers.

The Trial Balance is calculated entirely from posted Journal Lines and forms the basis for financial statements.

---

# Specification Structure

Every Business Object specification follows a consistent structure.

* Purpose
* Responsibilities
* Business Attributes
* Validation Rules
* Business Rules
* Relationships
* Lifecycle
* Status Definitions
* API Endpoints
* Permissions
* Events
* Reporting Impact
* Examples
* Future Enhancements

This standardized structure ensures consistency across the Accounting Engine and aligns with the documentation standards used throughout AaramBooks.

---

# Design Principles

All Accounting Business Objects follow these principles:

* Double Entry Accounting
* Deterministic Posting
* Immutable Financial Records
* Complete Auditability
* Event-Driven Processing
* Idempotent Execution
* Separation of Business Logic and Accounting Logic

Business Objects should not duplicate responsibilities that belong to another domain.

---

# Implementation Order

Business Objects should be implemented in the following sequence:

1. Ledger
2. Journal Entry
3. Journal Line
4. Account Mapping
5. Posting Rule
6. Financial Period
7. Trial Balance

Each Business Object should be fully implemented—including Models, Schemas, Repositories, Services, APIs, Tests, and Documentation—before proceeding to the next.

---

# Versioning

Business Object specifications evolve alongside the Accounting Engine.

Changes should preserve backward compatibility whenever possible.

Any breaking changes to accounting behavior or posting logic must be documented and reflected in the project CHANGELOG.

---

# Guiding Principle

The Accounting Engine is built around one central concept:

**Every financial transaction originates from a verified business event and is recorded through balanced, immutable Journal Entries.**

All financial reports, ledger balances, and external accounting exports are derived from these accounting records.
