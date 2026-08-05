# Posting Rule

## Purpose

The Posting Rule Business Object defines how verified business events are transformed into accounting transactions.

It determines when Journal Entries should be generated, which Account Mapping should be applied, and under what conditions financial transactions may be posted.

Posting Rules encapsulate accounting logic while remaining independent of business logic.

This separation allows business processes to evolve without requiring changes to the accounting engine.

---

# Responsibilities

Posting Rule is responsible for:

* Determining when Journal Entries should be created.
* Selecting the appropriate Account Mapping.
* Validating posting conditions.
* Supporting automated accounting.
* Providing configurable accounting behavior.

Posting Rule is **not** responsible for:

* Creating business documents.
* Managing Ledgers.
* Recording Journal Lines.
* Updating Inventory.
* Importing external data.

---

# Business Attributes

## Identification

| Attribute   | Description                |
| ----------- | -------------------------- |
| Rule Code   | Unique business identifier |
| Rule Name   | Display name               |
| Description | Optional description       |

---

## Business Event

| Attribute     | Description                        |
| ------------- | ---------------------------------- |
| Event Type    | Business event triggering the rule |
| Document Type | Related business document          |
| Event Source  | Operations, Inventory, Matching    |

Examples:

* Sales Invoice Posted
* Payment Received
* Settlement Received
* Customer Return
* Inventory Adjustment
* Purchase Receipt
* Stock Write-off

---

## Posting Configuration

| Attribute       | Description                   |
| --------------- | ----------------------------- |
| Account Mapping | Mapping used for posting      |
| Posting Trigger | Event that activates the rule |
| Auto Post       | Yes/No                        |

---

## Status

| Attribute | Description       |
| --------- | ----------------- |
| Status    | Active / Inactive |

---

## Audit Information

| Attribute  | Description |
| ---------- | ----------- |
| Created By | User/System |
| Created On | Timestamp   |
| Updated By | User/System |
| Updated On | Timestamp   |

---

# Validation Rules

* Rule Code must be unique.
* Rule Name must be unique.
* Event Type is mandatory.
* Account Mapping is mandatory.
* Posting Trigger is mandatory.
* Status is mandatory.

---

# Business Rules

## Rule 1

Every automated Journal Entry must be generated through a Posting Rule.

---

## Rule 2

Posting Rules must reference exactly one Account Mapping.

---

## Rule 3

Only Active Posting Rules may generate Journal Entries.

---

## Rule 4

Posting Rules must execute only after the originating business event has been successfully completed.

Example:

A Sales Order alone does not create accounting.

Accounting is generated only after the configured posting event (for example, Tax Invoice Posted or Order Completed).

---

## Rule 5

Posting Rules must be deterministic.

The same business event under the same conditions must always produce the same Journal Entry.

---

## Rule 6

Posting Rules do not contain Ledger information directly.

They delegate Ledger selection to the Account Mapping Business Object.

---

## Rule 7

Posting Rules must be idempotent.

The same business event must never generate duplicate Journal Entries.

---

## Rule 8

Deleting Posting Rules is prohibited.

Rules may only be marked as Inactive.

---

## Rule 9

Authoritative external financial data always takes precedence over internally derived estimates.

Gateway GST must be sourced directly from the payment gateway's authoritative records (e.g., Razorpay's `tax` column).

The Accounting Engine must never estimate gateway GST if the source system provides the exact value.

---

# Relationships

Posting Rule relates to:

* Account Mapping
* Journal Entry
* Journal Line
* Ledger
* Financial Period

---

# Lifecycle

```text id="p6f7jw"
ACTIVE

↓

INACTIVE
```

Inactive rules remain available for audit purposes but cannot generate new Journal Entries.

---

# Posting Workflow

```text id="g8lvnn"
Business Event

↓

Posting Rule

↓

Validation

↓

Account Mapping

↓

Journal Entry

↓

Journal Lines

↓

Ledger Balances Updated
```

---

# Reporting Impact

Posting Rules do not appear directly in financial reports.

They influence:

* Journal Register
* General Ledger
* Trial Balance
* Profit & Loss Statement
* Balance Sheet

by determining how Journal Entries are generated.

---

# Examples

## Sales Invoice

Business Event

Sales Invoice Posted

Posting Rule

Generate Sales Journal

Account Mapping

Sales Mapping

Result

Journal Entry created with:

* Accounts Receivable (Debit)
* Sales (Credit)
* GST Output (Credit)

---

## Razorpay Settlement

Business Event

Settlement Received

Posting Rule

Generate Settlement Journal

Account Mapping

Settlement Mapping

Result

Journal Entry created with:

* Bank (Debit)
* Payment Gateway Charges (Debit)
* Accounts Receivable (Credit)

---

## Inventory Adjustment

Business Event

Stock Adjustment Completed

Posting Rule

Generate Inventory Adjustment Journal

Account Mapping

Inventory Adjustment Mapping

Result

Journal Entry generated based on whether inventory increased or decreased.

---

# Future Enhancements

Future versions may support:

* Conditional Posting Rules
* Rule priorities
* Effective date versioning
* Company-specific Posting Rules
* Marketplace-specific Posting Rules
* Warehouse-specific Posting Rules
* Approval-based posting
* Scheduled posting

---

# Guiding Principle

**Posting Rules determine *when* accounting happens, not *where* it is posted.**

They act as the orchestration layer between verified business events and the Accounting Engine, ensuring that Journal Entries are generated consistently, deterministically, and without embedding accounting logic inside operational business processes.
