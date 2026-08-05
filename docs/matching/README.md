# Matching Domain

## Purpose

The Matching Domain is responsible for establishing trusted relationships between business documents imported from multiple external systems.

External platforms such as ShopDeck, Razorpay, logistics partners, banks, and future marketplaces generate independent documents that describe different parts of the same business transaction.

The Matching Engine transforms these isolated documents into a connected business graph.

The Matching Domain never imports data and never generates accounting entries.

Its sole responsibility is to identify, validate, create, manage and maintain relationships between canonical business documents.

---

# Position in System Architecture

```
External Platforms
        │
        ▼
Data Ingestion
        │
        ▼
Operations Domain
        │
        ▼
====================
 Matching Domain
====================
        │
        ▼
Inventory Engine
Accounting Engine
Reporting Engine
```

---

# Responsibilities

The Matching Domain is responsible for:

- Matching Sales Orders to Tax Invoices
- Matching Payments to Sales Orders
- Matching Payments to Settlements
- Matching Refunds to Orders
- Matching Refunds to Payments
- Matching Settlements to Bank Credits
- Tracking unmatched documents
- Recording match confidence
- Maintaining audit history

The Matching Domain is NOT responsible for:

- Importing files
- Parsing CSVs
- Inventory calculations
- Accounting entries
- GST calculations
- Journal generation

---

# Business Objects

## Match Job

Represents one execution of the matching engine.

Example:

```
Match Job
----------
Id
Started On
Completed On
Status

Orders Processed
Payments Processed
Settlements Processed

Successful Matches
Failed Matches
```

---

## Match Result

Represents one successful relationship.

Examples

```
Sales Order
↓

Tax Invoice
```

```
Payment
↓

Settlement
```

```
Settlement
↓

Bank Transaction
```

---

## Match Exception

Represents documents that could not be matched.

Examples

```
Payment without Order

Settlement without Payment

Invoice without Order

Refund without Payment
```

These exceptions remain open until resolved.

---

# Matching Strategy

Version 1 uses deterministic matching only.

No fuzzy logic.

No AI.

No assumptions.

Every successful match must be explainable.

---

# Matching Rules

## Sales Order ↔ Tax Invoice

Primary Key

External Order Id

---

## Payment ↔ Settlement

Primary Key

Settlement Id

---

## Settlement ↔ Bank

Primary Key

UTR Number

---

## Refund ↔ Payment

Primary Key

Payment Reference

---

# Match Status

Every document may have one of the following statuses.

```
UNMATCHED

PARTIALLY_MATCHED

MATCHED

EXCEPTION

MANUALLY_MATCHED
```

---

# Manual Matching

Users may manually resolve unmatched documents.

Every manual action must record:

- User
- Timestamp
- Previous State
- New State
- Reason

Manual matching must never overwrite imported source data.

---

# Matching Workflow

```
Operations Documents

↓

Create Match Job

↓

Run Matching Rules

↓

Create Match Results

↓

Create Match Exceptions

↓

Generate Match Summary
```

---

# Match Summary

Each Match Job produces a summary.

Example

```
Orders

250

Invoices

250

Payments

248

Settlements

6

Matched

245

Unmatched

5

Exceptions

3
```

---

# Events

The Matching Domain publishes business events.

Examples

```
OrderMatched

PaymentMatched

SettlementMatched

RefundMatched

MatchFailed

ManualMatchCreated
```

Future domains subscribe to these events.

Inventory Engine

Accounting Engine

Reporting Engine

---

# Design Principles

The Matching Engine must always be:

Deterministic

Explainable

Auditable

Idempotent

Repeatable

No business document may be modified during matching.

Matching only creates relationships.

Original business documents remain immutable.

---

# Future Roadmap

Version 1

Deterministic matching

Version 2

Rule-based matching

Version 3

Confidence scoring

Version 4

AI-assisted matching recommendations

Version 5

Machine learning optimization
