# Ledger

## Purpose

The Ledger Business Object represents an accounting account used to classify and record the financial impact of business transactions.

Every Journal Line must reference exactly one Ledger.

The Ledger serves as the permanent financial classification for all accounting entries and forms the foundation of the General Ledger, Trial Balance, Profit & Loss Statement, and Balance Sheet.

The Ledger is the fundamental building block of the Accounting Engine.

---

# Responsibilities

The Ledger is responsible for:

* Classifying financial transactions.
* Organizing accounting data.
* Maintaining account hierarchy.
* Supporting financial reporting.
* Supporting account mapping.
* Providing balances for financial statements.

The Ledger is **not** responsible for:

* Creating Journal Entries.
* Posting accounting transactions.
* Generating accounting rules.
* Importing accounting data.
* Exporting accounting data.

---

# Business Attributes

## Identification

| Attribute   | Description                |
| ----------- | -------------------------- |
| Ledger Code | Unique business identifier |
| Ledger Name | Ledger display name        |
| Description | Optional description       |

---

## Classification

| Attribute     | Description                               |
| ------------- | ----------------------------------------- |
| Ledger Type   | Asset, Liability, Equity, Income, Expense |
| Ledger Group  | Parent classification                     |
| Parent Ledger | Optional parent account                   |

---

## Financial Information

| Attribute       | Description                              |
| --------------- | ---------------------------------------- |
| Opening Balance | Opening balance for the financial period |
| Current Balance | Calculated running balance               |
| Normal Balance  | Debit or Credit                          |

---

## Status

| Attribute | Description        |
| --------- | ------------------ |
| Status    | Active or Inactive |

Inactive Ledgers remain available for historical reporting but cannot receive new Journal Lines.

---

## Audit Information

| Attribute  | Description |
| ---------- | ----------- |
| Created By | User/System |
| Created On | Timestamp   |
| Updated By | User/System |
| Updated On | Timestamp   |

---

# Ledger Types

Every Ledger belongs to one of the following types.

| Ledger Type | Description                     |
| ----------- | ------------------------------- |
| ASSET       | Resources owned by the business |
| LIABILITY   | Business obligations            |
| EQUITY      | Owner's interest                |
| INCOME      | Revenue earned                  |
| EXPENSE     | Costs incurred                  |

---

# Examples

## Asset

* Bank
* Cash
* Inventory
* Accounts Receivable

---

## Liability

* Accounts Payable
* GST Payable
* Outstanding Expenses

---

## Equity

* Capital
* Retained Earnings

---

## Income

* Sales
* Shipping Income
* Other Income

---

## Expense

* Cost of Goods Sold
* Freight Expense
* Payment Gateway Charges
* Packaging Expense
* Advertising Expense

---

# Validation Rules

* Ledger Code must be unique.
* Ledger Name must be unique.
* Ledger Type is mandatory.
* Ledger Group is mandatory.
* Normal Balance is mandatory.
* Status is mandatory.

---

# Business Rules

## Rule 1

Ledger Code is immutable.

It cannot be modified after creation.

---

## Rule 2

Ledger Name must remain unique.

---

## Rule 3

Every Journal Line must reference one Ledger.

---

## Rule 4

Inactive Ledgers cannot receive new Journal Entries.

Historical entries remain unchanged.

---

## Rule 5

Ledger balances are calculated from posted Journal Lines.

Balances must never be edited directly.

---

## Rule 6

A Ledger cannot be deleted.

If no longer required, it must be marked as Inactive.

---

## Rule 7

Parent-child relationships may be used to organize financial reports but do not affect posting logic.

---

# Relationships

The Ledger Business Object relates to:

* Journal Entry
* Journal Line
* Account Mapping
* Trial Balance
* Financial Period

---

# Lifecycle

```text id="uaxqx9"
ACTIVE

↓

INACTIVE
```

Ledgers are never deleted.

---

# Permissions

| Action            | Permission       |
| ----------------- | ---------------- |
| Create Ledger     | Administrator    |
| Update Ledger     | Administrator    |
| Activate Ledger   | Administrator    |
| Inactivate Ledger | Administrator    |
| View Ledger       | Authorized Users |

Deletion is never permitted.

---

# Reporting Impact

Ledgers contribute to:

* General Ledger
* Trial Balance
* Profit & Loss Statement
* Balance Sheet
* GST Reports
* Financial Dashboard

---

# Examples

## Sales Ledger

| Field          | Value     |
| -------------- | --------- |
| Ledger Code    | LED-SALES |
| Ledger Name    | Sales     |
| Ledger Type    | INCOME    |
| Normal Balance | CREDIT    |

---

## Inventory Ledger

| Field          | Value           |
| -------------- | --------------- |
| Ledger Code    | LED-INVENTORY   |
| Ledger Name    | Inventory Asset |
| Ledger Type    | ASSET           |
| Normal Balance | DEBIT           |

---

## Bank Ledger

| Field          | Value     |
| -------------- | --------- |
| Ledger Code    | LED-BANK  |
| Ledger Name    | Axis Bank |
| Ledger Type    | ASSET     |
| Normal Balance | DEBIT     |

---

# Future Enhancements

Future versions may support:

* Multi-company chart of accounts
* Cost centers
* Profit centers
* Branch-wise ledgers
* Multi-currency ledgers
* Budget tracking
* Consolidated reporting

---

# Guiding Principle

**Every accounting transaction must be classified through a Ledger.**

Ledgers define *where* financial transactions are recorded, while Journal Entries define *what* happened. Together they form the foundation of the AaramBooks Accounting Engine.
