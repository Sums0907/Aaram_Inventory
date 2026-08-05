# Account Mapping

## Purpose

The Account Mapping Business Object defines how business events are translated into accounting Ledgers.

It acts as the bridge between operational business events and financial accounting.

Rather than hardcoding Ledger references inside business logic, the Accounting Engine consults Account Mapping to determine which Ledgers should be used for each accounting transaction.

This allows accounting behavior to be configured without modifying application code.

---

# Responsibilities

Account Mapping is responsible for:

* Mapping business events to Ledgers.
* Supporting configurable accounting rules.
* Separating accounting configuration from business logic.
* Supporting multiple accounting scenarios.
* Providing the foundation for automated Journal generation.

Account Mapping is **not** responsible for:

* Creating Journal Entries.
* Posting Journal Lines.
* Managing Ledgers.
* Calculating financial balances.
* Importing business documents.

---

# Business Attributes

## Identification

| Attribute    | Description                |
| ------------ | -------------------------- |
| Mapping Code | Unique business identifier |
| Mapping Name | Display name               |
| Description  | Optional description       |

---

## Business Event

| Attribute        | Description                          |
| ---------------- | ------------------------------------ |
| Event Type       | Business event triggering accounting |
| Document Type    | Related business document            |
| Transaction Type | Optional subtype                     |

Examples:

* Sale
* Customer Return
* Settlement
* Payment
* Refund
* Inventory Adjustment
* Purchase
* Stock Write-off

---

## Ledger Configuration

For each accounting component:

| Attribute     | Description      |
| ------------- | ---------------- |
| Debit Ledger  | Ledger to debit  |
| Credit Ledger | Ledger to credit |

A single business event may require multiple Debit and Credit Ledgers.

---

## Status

| Attribute | Description       |
| --------- | ----------------- |
| Status    | Active / Inactive |

Inactive mappings cannot be used for new Journal Entries.

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

* Mapping Code must be unique.
* Mapping Name must be unique.
* Event Type is mandatory.
* At least one Debit Ledger is required.
* At least one Credit Ledger is required.
* Status is mandatory.

---

# Business Rules

## Rule 1

Every automated Journal Entry must use an Account Mapping.

---

## Rule 2

Business logic must never reference Ledger codes directly.

Ledger selection must always occur through Account Mapping.

---

## Rule 3

Mappings may contain multiple Debit and Credit Ledgers.

Example:

```text id="6myk7z"
Sale

↓

Accounts Receivable (Debit)

Sales (Credit)

GST Output (Credit)
```

---

## Rule 4

Only Active mappings may generate Journal Entries.

---

## Rule 5

Historical Journal Entries remain unchanged even if an Account Mapping is modified later.

---

## Rule 6

Deleting Account Mappings is prohibited.

Mappings may only be marked as Inactive.

---

# Relationships

Account Mapping relates to:

* Ledger
* Posting Rule
* Journal Entry
* Journal Line

---

# Lifecycle

```text id="ks5v3s"
ACTIVE

↓

INACTIVE
```

Inactive mappings remain available for audit purposes.

---

# Mapping Workflow

```text id="u4x8pk"
Business Event

↓

Account Mapping

↓

Posting Rule

↓

Journal Entry

↓

Journal Lines
```

---

# Reporting Impact

Account Mappings indirectly affect:

* Journal Register
* General Ledger
* Trial Balance
* Profit & Loss Statement
* Balance Sheet

They are configuration objects and do not appear directly in financial reports.

---

# Examples

## Sale

| Accounting Component | Ledger              |
| -------------------- | ------------------- |
| Debit                | Accounts Receivable |
| Credit               | Sales               |
| Credit               | GST Output          |

---

## Razorpay Settlement

| Accounting Component | Ledger                  |
| -------------------- | ----------------------- |
| Debit                | Bank                    |
| Debit                | Payment Gateway Charges |
| Credit               | Accounts Receivable     |

---

## Inventory Adjustment

| Accounting Component | Ledger                    |
| -------------------- | ------------------------- |
| Debit                | Inventory Asset           |
| Credit               | Inventory Adjustment Gain |

or

| Accounting Component | Ledger                    |
| -------------------- | ------------------------- |
| Debit                | Inventory Adjustment Loss |
| Credit               | Inventory Asset           |

Depending on whether stock increased or decreased.

---

# Future Enhancements

Future versions may support:

* Company-specific mappings
* Channel-specific mappings
* Marketplace-specific mappings
* Warehouse-specific mappings
* Conditional mappings
* Effective date versioning
* Rule priorities

---

# Guiding Principle

**Business events should never know where they are posted in the Chart of Accounts.**

Account Mapping isolates accounting configuration from business logic, enabling AaramBooks to generate consistent, configurable, and maintainable accounting entries while preserving complete auditability.
