# Financial Period

## Purpose

The Financial Period Business Object represents a defined accounting period during which financial transactions may be recorded.

Financial Periods control when Journal Entries can be created, posted, modified, and reported.

They ensure financial statements remain consistent by preventing postings into closed accounting periods.

The Financial Period serves as the accounting calendar for the AaramBooks platform.

---

# Responsibilities

The Financial Period is responsible for:

* Defining accounting periods.
* Controlling Journal Entry posting.
* Supporting month-end and year-end closing.
* Preventing posting into closed periods.
* Maintaining accounting chronology.
* Supporting financial reporting.

The Financial Period is **not** responsible for:

* Creating Journal Entries.
* Maintaining Ledgers.
* Posting accounting transactions.
* Calculating financial reports.
* Importing financial data.

---

# Business Attributes

## Identification

| Attribute   | Description                |
| ----------- | -------------------------- |
| Period Code | Unique business identifier |
| Period Name | Display name               |

Examples:

* FY2026-27
* Apr-2026
* May-2026

---

## Period Dates

| Attribute  | Description                    |
| ---------- | ------------------------------ |
| Start Date | Beginning of accounting period |
| End Date   | End of accounting period       |

---

## Financial Information

| Attribute       | Description                     |
| --------------- | ------------------------------- |
| Financial Year  | Parent financial year           |
| Period Sequence | Order within the financial year |

---

## Status

| Attribute | Description              |
| --------- | ------------------------ |
| Status    | Current lifecycle status |

---

## Audit Information

| Attribute  | Description |
| ---------- | ----------- |
| Created By | User/System |
| Created On | Timestamp   |
| Closed By  | User/System |
| Closed On  | Timestamp   |

---

# Period Status

The Accounting Engine supports the following statuses.

| Status | Description                          |
| ------ | ------------------------------------ |
| OPEN   | Transactions may be posted           |
| CLOSED | No new transactions permitted        |
| LOCKED | Historical period permanently locked |

---

# Validation Rules

* Period Code must be unique.
* Period Name must be unique.
* Start Date is mandatory.
* End Date is mandatory.
* End Date must be greater than Start Date.
* Financial Year is mandatory.
* Status is mandatory.

---

# Business Rules

## Rule 1

Every Journal Entry belongs to exactly one Financial Period.

---

## Rule 2

Journal Entries may only be posted into OPEN periods.

---

## Rule 3

CLOSED periods prohibit new Journal Entries but remain available for reporting.

---

## Rule 4

LOCKED periods cannot be reopened except through authorized administrative procedures.

---

## Rule 5

Financial Periods must not overlap.

---

## Rule 6

A Financial Period cannot be closed while Draft or Unposted Journal Entries exist within that period.

---

## Rule 7

Closing a Financial Period does not modify historical Journal Entries.

It only prevents future postings.

---

## Rule 8

Deleting Financial Periods is prohibited.

Financial history must always remain intact.

---

# Relationships

Financial Period relates to:

* Journal Entry
* Journal Line
* Ledger
* Trial Balance

---

# Lifecycle

```text id="jq9dxf"
OPEN

↓

CLOSED

↓

LOCKED
```

Once LOCKED, the period is considered final for reporting purposes.

---

# Period Closing Workflow

```text id="g7n2ux"
Accounting Period Open

↓

Journal Entries Posted

↓

Financial Review

↓

Period Closed

↓

Period Locked

↓

Next Period Opened
```

---

# Reporting Impact

Financial Periods determine the reporting boundaries for:

* General Ledger
* Journal Register
* Trial Balance
* Profit & Loss Statement
* Balance Sheet
* GST Reports

---

# Examples

## April 2026

| Field       | Value       |
| ----------- | ----------- |
| Period Code | APR-2026    |
| Start Date  | 01-Apr-2026 |
| End Date    | 30-Apr-2026 |
| Status      | OPEN        |

Result

Journal Entries dated within April 2026 may be posted.

---

## March 2026

| Field       | Value       |
| ----------- | ----------- |
| Period Code | MAR-2026    |
| Start Date  | 01-Mar-2026 |
| End Date    | 31-Mar-2026 |
| Status      | CLOSED      |

Result

Historical reports remain available, but no additional Journal Entries may be posted.

---

# Future Enhancements

Future versions may support:

* Multi-company financial calendars
* Fiscal calendars
* Period reopening with approval
* Soft close and hard close
* Automatic period creation
* Automated year-end closing
* Multi-currency financial periods

---

# Guiding Principle

**Financial transactions must be recorded only within valid accounting periods.**

Financial Periods preserve the integrity of financial reporting by ensuring that historical accounting records remain stable while allowing new business activity to be recorded in the appropriate reporting period.
