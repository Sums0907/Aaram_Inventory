# Journal Entry

## Purpose

The Journal Entry Business Object represents a complete accounting transaction generated from a verified business event.

Every financial event within AaramBooks—such as a sale, payment, settlement, refund, inventory adjustment, or purchase—results in one or more Journal Entries.

A Journal Entry consists of one or more Journal Lines and must always satisfy the principles of Double Entry Accounting.

Journal Entries are immutable once posted.

---

# Responsibilities

Journal Entry is responsible for:

* Recording accounting transactions.
* Maintaining complete accounting history.
* Grouping Journal Lines into a single financial event.
* Ensuring accounting transactions remain balanced.
* Providing traceability to business documents.
* Supporting financial reporting.

Journal Entry is **not** responsible for:

* Defining Ledgers.
* Posting individual debit or credit amounts.
* Generating accounting rules.
* Importing financial data.
* Exporting accounting data.

---

# Business Attributes

## Identification

| Attribute      | Description                |
| -------------- | -------------------------- |
| Journal Number | Unique business identifier |
| Journal Date   | Accounting date            |
| Posting Date   | Financial posting date     |
| Status         | Journal lifecycle          |

---

## Source Information

| Attribute              | Description                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| Source Domain          | Operations, Inventory, Matching                                             |
| Source Document Type   | Sales Order, Tax Invoice, Settlement, Payment, Refund, Inventory Adjustment |
| Source Document Number | Business document reference                                                 |
| Source Document ID     | Internal UUID                                                               |

---

## Journal Information

| Attribute        | Description                   |
| ---------------- | ----------------------------- |
| Description      | Journal narration             |
| Financial Period | Accounting period             |
| Currency         | Transaction currency          |
| Exchange Rate    | Future multi-currency support |

---

## Summary Information

| Attribute    | Description             |
| ------------ | ----------------------- |
| Total Debit  | Sum of all debit lines  |
| Total Credit | Sum of all credit lines |

---

## Audit Information

| Attribute  | Description |
| ---------- | ----------- |
| Created By | User/System |
| Created On | Timestamp   |
| Posted By  | User/System |
| Posted On  | Timestamp   |

---

# Validation Rules

* Journal Number must be unique.
* Journal Date is mandatory.
* Posting Date is mandatory.
* Financial Period is mandatory.
* Status is mandatory.
* Journal must contain at least two Journal Lines.
* Total Debit must equal Total Credit.

---

# Business Rules

## Rule 1

Every Journal Entry must originate from a verified business event.

Manual creation should only be allowed for approved adjustment journals.

---

## Rule 2

Every Journal Entry must be balanced.

```text id="jjc7cf"
Total Debit

=

Total Credit
```

Unbalanced Journal Entries cannot be posted.

---

## Rule 3

Journal Entries are immutable after posting.

Corrections must be made through reversing or adjustment Journal Entries.

---

## Rule 4

A Journal Entry must belong to one Financial Period.

---

## Rule 5

Every Journal Entry must reference the originating business document.

Complete traceability is mandatory.

---

## Rule 6

A Journal Entry may contain multiple Journal Lines.

There is no fixed limit.

---

## Rule 7

Deleting Journal Entries is prohibited.

Historical financial records must always be preserved.

---

# Relationships

Journal Entry relates to:

* Ledger
* Journal Line
* Posting Rule
* Account Mapping
* Financial Period
* Trial Balance

---

# Lifecycle

```text id="lz7kmy"
DRAFT

↓

VALIDATED

↓

POSTED

↓

REVERSED
```

Only POSTED Journal Entries affect ledger balances.

---

# Posting Workflow

```text id="a3xjmt"
Business Event

↓

Posting Rule

↓

Journal Entry Created

↓

Validation

↓

Journal Posted

↓

Ledger Updated

↓

Trial Balance Updated
```

---

# Reporting Impact

Journal Entries contribute to:

* Journal Register
* General Ledger
* Trial Balance
* Profit & Loss Statement
* Balance Sheet
* GST Reports
* Financial Dashboard

---

# Examples

## Sale Journal

Business Event

Sales Invoice

Journal Number

JE-000145

Description

Sales Invoice INV-000145

Journal Lines

| Ledger              |  Debit | Credit |
| ------------------- | -----: | -----: |
| Accounts Receivable | 11,800 |      0 |
| Sales               |      0 | 10,000 |
| GST Output          |      0 |  1,800 |

Result

* Total Debit = ₹11,800
* Total Credit = ₹11,800

Balanced ✅

---

## Settlement Journal

Business Event

Razorpay Settlement

Journal Lines

| Ledger                  | Debit | Credit |
| ----------------------- | ----: | -----: |
| Bank                    | 9,700 |      0 |
| Payment Gateway Charges |   300 |      0 |
| Accounts Receivable     |     0 | 10,000 |

Balanced ✅

---

# Future Enhancements

Future versions may support:

* Recurring Journal Entries
* Multi-currency Journals
* Auto-reversing Journals
* Inter-company Journals
* Consolidation Journals
* Approval Workflows

---

# Guiding Principle

**Every financial event is recorded through a balanced Journal Entry.**

Journal Entries are immutable, fully traceable, and always linked to the originating business event, ensuring complete financial integrity throughout the AaramBooks platform.
