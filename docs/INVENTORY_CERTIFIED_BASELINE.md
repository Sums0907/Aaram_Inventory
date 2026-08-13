# AaramBooks Inventory Certified Baseline
**Date:** 2026-08-12
**Status:** FULLY CERTIFIED & ISOLATED

This document serves as the **"do not break this" contract** for the AaramBooks Inventory system. It outlines the rigid database environments, safety rules, and functional invariants that have been formally certified.

## 1. Database Environments
AaramBooks enforces a strict separation of database environments to ensure data integrity and safety.

- **DEVELOPMENT**: The manual working environment containing user-entered data (`test_manual.db`).
- **TEST**: Ephemeral, disposable environments exclusively used by automated certification scripts (`test_cert_*.db`, `test_bom.db`, etc.).
- **PRODUCTION**: The live production environment.

## 2. Protected Development DB
The development database (`test_manual.db`) is **PROTECTED**.
- **No Destructive Operations**: `drop_all()` and bulk `session.execute(delete(...))` operations are entirely blocked via SQLAlchemy event listeners (`safety.py`).
- **No Test Pollution**: Automated tests and certification scripts are forbidden from writing to or modifying `test_manual.db`.

## 3. Golden Backup Location
A secure, "known-good" golden backup of the development database is stored **outside** the project workspace to protect it from any automated cleanup or reset scripts.
- **Path**: `~/.aarambooks_golden_backup/dev_golden_post_restoration_20260812.db`
- **Rule**: If the development database is ever corrupted or deleted, DO NOT run reset scripts. Immediately restore from this golden backup.

## 4. Certification Suites
The inventory system's integrity is guaranteed by four standalone certification suites, each running against its own isolated disposable database:
1. `certify_bom_module.py`
2. `certify_inventory_truth.py`
3. `certify_daily_inventory_update.py`
4. `certify_job_worker_allocation.py`

## 5. Certification Result
**OVERALL CERTIFICATION: PASS**
- BOM Module: PASS
- Inventory Truth: PASS
- Daily Inventory Update: PASS
- Job Worker Allocation: PASS
- Database Safety & Isolation: PASS
- Mathematical Precision: PASS
- Transaction Atomicity: PASS
- Historical Integrity: PASS

## 6. Job Worker Accounting Addendum
The Job Worker Rate Master is governed by strict strict rules guaranteeing **exactly one Active Rate** per (Worker, Product) pair. All rate revisions are atomic and archive the previous rate, leaving historical Job Work Expenses untouched.
See [Job Worker Accounting Rules](accounting/JOB_WORKER_ACCOUNTING.md) for full architectural details.
- Job Work Return: PASS
- Multiple/Partial Receipts: PASS
- FIFO Allocation: PASS

## 6. Inventory Transformation Engine Rules
The `InventoryTransformationEngine` enforces the following invariants:
- BOM validation is mandatory before receiving Job Work.
- Raw materials must be consumed using strict Decimal precision.
- FIFO allocation must be strictly adhered to against specific Job Work Issues.
- An immutable `InventoryTransformationRecord` must be created for every transformation.

## 7. Job Worker Ledger Rules
**Job Worker Inventory ≠ Finished Goods Inventory**
- The Job Worker ledger strictly maintains custody as: **Job Worker × Inventory Item**.
- A separate item ledger is used for Job Workers rather than a mixed ledger.
- Raw materials are transferred to Job Workers via `JobWorkIssueModel` and consumed via `JobWorkAllocationModel`.

## 8. BOM (Bill of Materials) Rules
- BOM snapshots must remain historically intact. Changes to a BOM do not retroactively affect past productions or job work receipts.
- Raw material consumption mathematically follows the specified BOM quantities per unit, ensuring exact raw material debiting based on the finished goods quantity received.

## 9. Finished Goods Isolation Rules
- Finished Goods purchased directly from other suppliers remain completely outside the Job Worker custody system.
- Standard Goods Receipts for Finished Goods update the main warehouse inventory without triggering the `InventoryTransformationEngine`.

## 10. Certification Script Prohibition Rules
- **No Test Data in Dev**: Certification scripts are prohibited from touching development (`test_manual.db`) or production databases.
- **Explicit Ownership**: A certification script may destroy ONLY a TEST database that it explicitly owns.
- **Enforcement**: This is enforced by `DATABASE_ENV` checks and SQLAlchemy event listeners.
