# Journal Line

## Purpose

The Journal Line Business Object represents a single debit or credit posting within a Journal Entry.

Every Journal Entry consists of one or more Journal Lines.

Each Journal Line records the financial impact on exactly one Ledger.

Together, the Journal Lines within a Journal Entry must satisfy the principles of Double Entry Accounting.

Journal Lines are immutable once the parent Journal Entry is posted.

---

# Responsibilities

Journal Line is responsible for:

* Recording debit postings.
* Recording credit postings.
* Linking financial amounts to Ledgers.
* Supporting General Ledger reporting.
* Supporting Trial Balance calculations.
* Providing complete financial traceability.

Journal Line is **not** responsible for:

* Creating Journal Entries.
* Defining Ledgers.
* Applying posting rules.
* Maintaining account balances.
* Generating financial reports.

---

# Business Attributes

## Identification

| Attribute     | Description                                |
| ------------- | ------------------------------------------ |
| Line Number   | Sequential number within the Journal Entry |
| Journal Entry | Parent Journal Entry                       |

---

## Ledger Information

| Attribute   | Description         |
| ----------- | ------------------- |
| Ledger      | Accounting Ledger   |
| Ledger Code | Business identifier |
| Ledger Name | Display name        |

---

## Financial Information

| Attribute     | Description                   |
| ------------- | ----------------------------- |
| Debit Amount  | Debit value                   |
| Credit Amount | Credit value                  |
| Currency      | Transaction currency          |
| Exchange Rate | Future multi-currency support |

---

## Description

| Attribute | Description               |
| --------- | ------------------------- |
| Narration | Optional line description |

---

## Source Information

| Attribute              | Description                   |
| ---------------------- | ----------------------------- |
| Source Document Type   | Originating business document |
| Source Document Number | Reference document            |

---

## Audit Information

| Attribute  | Description |
| ---------- | ----------- |
| Created By | User/System |
| Created On | Timestamp   |

---

# Validation Rules

* Journal Entry is mandatory.
* Ledger is mandatory.
* Either Debit Amount or Credit Amount must be greater than zero.
* Debit Amount and Credit Amount cannot both be greater than zero.
* Debit Amount cannot be negative.
* Credit Amount cannot be negative.

---

# Business Rules

## Rule 1

Every Journal Line belongs to exactly one Journal Entry.

---

## Rule 2

Every Journal Line references exactly one Ledger.

---

## Rule 3

A Journal Line must represent either a Debit or a Credit.

Never both.

```text id="j3d2vk"
✓ Debit = 100
  Credit = 0

✓ Debit = 0
  Credit = 100

✗ Debit = 100
  Credit = 100
```

---

## Rule 4

Journal Lines cannot exist independently.

They are always created as part of a Journal Entry.

---

## Rule 5

Journal Lines become immutable once the parent Journal Entry is posted.

---

## Rule 6

Deleting Journal Lines is prohibited.

Financial history must always remain intact.

---

## Rule 7

The sum of all Debit Journal Lines within a Journal Entry must equal the sum of all Credit Journal Lines.

This validation is performed at the Journal Entry level.

---

# Relationships

Journal Line relates to:

* Journal Entry
* Ledger
* Financial Period
* Trial Balance

---

# Lifecycle

```text id="m6x1vz"
CREATED

↓

POSTED

↓

REVERSED
```

Journal Lines inherit their lifecycle from the parent Journal Entry.

---

# Posting Workflow

```text id="6axpzc"
Business Event

↓

Journal Entry

↓

Journal Lines

↓

Ledger Balances Updated

↓

Trial Balance Updated
```

---

# Reporting Impact

Journal Lines contribute to:

* General Ledger
* Trial Balance
* Journal Register
* Profit & Loss Statement
* Balance Sheet
* GST Reports

---

# Examples

## Sales Invoice

| Ledger              |  Debit | Credit |
| ------------------- | -----: | -----: |
| Accounts Receivable | 11,800 |      0 |
| Sales               |      0 | 10,000 |
| GST Output          |      0 |  1,800 |

Three Journal Lines belong to one Journal Entry.

---

## Razorpay Settlement

| Ledger                  | Debit | Credit |
| ----------------------- | ----: | -----: |
| Bank                    | 9,700 |      0 |
| Payment Gateway Charges |   300 |      0 |
| Accounts Receivable     |     0 | 10,000 |

Again, three Journal Lines make up a balanced Journal Entry.

---

# Future Enhancements

Future versions may support:

* Multi-currency Journal Lines
* Cost Center allocation
* Profit Center allocation
* Project allocation
* Branch allocation
* Tax dimensions
* Analytical dimensions

---

# Guiding Principle

**A Journal Line represents the smallest accounting event within AaramBooks.**

Every debit and every credit is recorded as an individual Journal Line against exactly one Ledger. Financial reports, ledger balances, and trial balances are all derived from the complete collection of posted Journal Lines.
