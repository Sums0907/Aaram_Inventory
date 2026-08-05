# Version 1 Demonstration (MVP)

## Purpose

The Version 1 Demonstration represents the first complete implementation of the AaramBooks business workflow.

Unlike previous milestones, which focused on individual domains and architectural foundations, this phase validates that all implemented domains work together as a single, coherent business application.

The objective is to prove that AaramBooks can process real ShopDeck business data and generate production-ready accounting records suitable for import into Vyapar.

This milestone marks the transition from **architecture** to **product**.

---

# Objectives

The Version 1 Demonstration aims to:

* Demonstrate the complete end-to-end workflow.
* Validate business correctness using the Golden Dataset.
* Generate accounting journals identical to the validated legacy implementation.
* Produce Vyapar-compatible exports.
* Expose business information through simple APIs.
* Provide a repeatable demonstration of the system.

---

# Scope

The Version 1 Demonstration includes:

* Connector Framework
* Data Ingestion
* Operations
* Matching
* Inventory
* Accounting
* Verification
* Business Summary
* Vyapar Export

No additional business domains are introduced.

Architecture remains frozen.

---

# Product Workflow

The complete business workflow is:

```text
ShopDeck Reports

↓

Connector Framework

↓

Data Ingestion

↓

Validation

↓

Approval

↓

Commit

↓

Operations

↓

Matching

↓

Inventory

↓

Accounting

↓

Verification

↓

Business Summary

↓

Vyapar Export
```

Every stage is independently testable while remaining part of a single integrated pipeline.

---

# Included Components

## Connector Framework

Responsible for:

* Marketplace synchronization
* Download history
* Duplicate detection
* Raw file storage
* Triggering Data Ingestion

The Connector Framework does not perform business processing.

---

## Data Ingestion

Responsible for:

* CSV parsing
* Validation
* Import Jobs
* Approval
* Commit

---

## Operations

Responsible for constructing canonical business documents.

Examples include:

* Sales Orders
* Tax Invoices
* Payments
* Settlements

---

## Matching

Responsible for establishing relationships between business documents.

Examples:

* Invoice → Sales Order
* Payment → Invoice
* Settlement → Payment

---

## Inventory

Responsible for:

* Inventory Movements
* Inventory Balances

Inventory represents the operational state of the business.

---

## Accounting

Responsible for:

* Journal Entries
* Journal Lines
* Monthly Journal Aggregation

Accounting is generated from validated business events.

---

## Verification

Responsible for validating the integrity of the complete business workflow.

Checks include:

* Golden Dataset
* Journal Balance
* Duplicate Detection
* Missing SKUs
* Missing Business Documents
* Accounting Consistency

The Verification phase determines whether processing is considered successful.

---

## Business Summary

Provides aggregated information for presentation layers.

Example metrics include:

* Orders Imported
* Sales Orders
* Tax Invoices
* Payments
* Settlements
* Inventory Movements
* Journal Entries
* Journal Lines
* Golden Dataset Status

Business Summary performs aggregation only.

Business logic remains within the individual domains.

---

## Vyapar Export

Generates production-ready accounting exports.

Current exports include:

* Sales Journal
* Credit Note Journal
* Settlement Journal

The exported data matches the validated accounting rules extracted from the legacy implementation.

---

# API Endpoints

## Dashboard

```text
GET /api/v1/dashboard/summary
```

Returns the aggregated business summary.

---

## Vyapar Export

```text
GET /api/v1/accounting/export/vyapar/sales

GET /api/v1/accounting/export/vyapar/credit-notes

GET /api/v1/accounting/export/vyapar/settlements
```

Each endpoint returns a single CSV suitable for import into Vyapar.

---

## Connector

```text
POST /api/v1/shopdeck/sync

GET /api/v1/shopdeck/status

GET /api/v1/shopdeck/history

GET /api/v1/shopdeck/reports
```

The ShopDeck connector currently provides the synchronization framework. Live report downloading will be completed once the authenticated ShopDeck communication mechanism is integrated.

---

# Demonstration Script

The Version 1 Demonstration is executed using:

```text
scripts/run_version1_demo.py
```

The demonstration behaves exactly like a frontend client by communicating exclusively through the public HTTP APIs.

No repositories or services are accessed directly.

---

# Demonstration Workflow

```text
Upload Reports

↓

Approve

↓

Commit

↓

Matching

↓

Inventory

↓

Accounting

↓

Verification

↓

Business Summary

↓

Vyapar Export

↓

Done
```

---

# Expected Demonstration Output

A successful execution should produce a summary similar to:

```text
================================================

AARAMBOOKS VERSION 1

================================================

Orders Imported

Sales Orders

Tax Invoices

Payments

Settlements

Matched Orders

Inventory Movements

Journal Entries

Journal Lines

Golden Dataset

PASS

Verification

PASS

Vyapar Export

PASS

================================================
```

This output represents the successful completion of the complete business workflow.

---

# Verification

The Version 1 Demonstration is considered successful only if all of the following pass:

* Golden Dataset verification
* Journal balance verification
* Debit equals Credit
* Duplicate detection
* Inventory consistency
* Business summary generation
* Vyapar export generation

Any failure invalidates the demonstration.

---

# Business Principles

The demonstration adheres to the following principles:

## Canonical Data Model

External reports are transformed into canonical business objects before any downstream processing.

---

## Deterministic Processing

Identical input data must always produce identical business outputs.

---

## Event-Driven Workflow

Business events trigger downstream processing without duplicating responsibilities across domains.

---

## Verification Before Presentation

Business data must pass verification before being presented through dashboards or exported to external systems.

---

# Success Criteria

The Version 1 Demonstration is complete when a user can:

1. Synchronize or upload ShopDeck reports.
2. Execute the complete processing pipeline.
3. Verify the Golden Dataset successfully.
4. View the Business Summary.
5. Export Vyapar-compatible monthly journals.
6. Import those journals into Vyapar without manual modification.

---

# Future Enhancements

The following features are intentionally outside the scope of Version 1:

* Live ShopDeck synchronization
* React Web Interface
* Scheduled Synchronization
* Advanced Reporting
* Dashboard Widgets
* Automation Engine
* AI Assistant
* Notifications
* Multi-marketplace integrations

These will build upon the stable foundation established by the Version 1 Demonstration.

---

# Definition of Done

Version 1 is considered complete when the entire monthly accounting workflow can be executed using real business data, producing verified accounting journals that match the trusted legacy implementation and are immediately importable into Vyapar.

---

# Guiding Principle

**Version 1 is not the end of development—it is the first proof that AaramBooks can replace a real monthly accounting workflow with a clean, verifiable, and scalable architecture.**
