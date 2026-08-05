# Marketplace Connector Engine

## Purpose

The Marketplace Connector Engine is responsible for securely connecting AaramBooks with external e-commerce platforms and automatically acquiring operational reports required for downstream business processing.

Unlike the Data Ingestion Engine, which processes files already available to the system, the Connector Engine is responsible for obtaining those files from external platforms.

The Connector Engine is the first stage of the AaramBooks processing pipeline.

---

# Vision

AaramBooks should eventually support multiple marketplaces through a common connector framework.

Current implementation target:

- ShopDeck

Future marketplaces:

- Amazon
- Flipkart
- Shopify
- Meesho
- WooCommerce
- Magento
- Custom APIs

The Connector Engine provides a common abstraction that allows every marketplace to integrate into the same downstream business pipeline.

---

# Responsibilities

The Connector Engine is responsible for:

- Authentication
- Session Management
- Report Download
- Duplicate Detection
- Secure Storage
- Synchronization History
- Automatic Import Triggering

The Connector Engine is NOT responsible for:

- CSV Parsing
- Validation
- Matching
- Accounting
- Inventory
- Reporting

Those responsibilities belong to downstream domains.

---

# Position in Architecture

```text
Marketplace

↓

Connector Engine

↓

Storage

↓

Data Ingestion

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

Dashboard

↓

Export
```

---

# Design Principles

## Single Responsibility

The Connector Engine only retrieves external business data.

Business interpretation is delegated to downstream systems.

---

## Marketplace Agnostic

Every marketplace connector must expose a common interface.

The rest of AaramBooks should never depend on marketplace-specific logic.

---

## Secure by Default

Credentials must never be hardcoded.

Secrets are loaded exclusively from configuration.

---

## Idempotent Synchronization

Running synchronization multiple times must never create duplicate imports.

Duplicate detection is mandatory.

---

## Auditability

Every downloaded report must be traceable.

Downloaded files must record:

- Marketplace
- Report Type
- Accounting Period
- Download Time
- Checksum
- Storage Path
- Synchronization Run

---

# Connector Architecture

```text
MarketplaceConnector

↓

ShopDeckConnector

↓

Future Connectors
```

The MarketplaceConnector defines the common interface.

Marketplace implementations contain only platform-specific communication.

---

# Synchronization Workflow

```text
User

↓

Sync Marketplace

↓

Authenticate

↓

Validate Session

↓

Download Reports

↓

Store Files

↓

Generate Checksums

↓

Duplicate Detection

↓

Register Download

↓

Trigger Data Ingestion

↓

Return Synchronization Summary
```

---

# Connector Lifecycle

## Step 1

Authenticate

Establish authenticated session.

---

## Step 2

Validate

Confirm credentials remain valid.

---

## Step 3

Discover

Determine reports available for the requested accounting period.

---

## Step 4

Download

Retrieve reports.

Streaming downloads are preferred.

---

## Step 5

Storage

Persist raw files.

No modification is performed.

---

## Step 6

Duplicate Detection

Generate checksum.

Compare against historical downloads.

Skip duplicates.

---

## Step 7

Import

Automatically trigger Data Ingestion.

---

## Step 8

Synchronization Report

Return synchronization summary.

---

# Downloaded Reports

Current ShopDeck reports:

## Order Reconciliation Report

Primary operational sales report.

---

## Tax Ready Report

Official GST breakdown.

---

## COD Settlement Report

Cash-on-Delivery settlements.

---

Future:

## Return Reports

## Cancellation Reports

## Inventory Reports

## Payout Reports

---

# Storage Layout

```text
storage/

marketplace/

shopdeck/

2026/

04/

order_reconciliation.csv

tax_ready.csv

cod_settlement.csv
```

Raw reports remain immutable.

---

# Authentication

The Connector Engine supports:

- Session Cookies
- Bearer Tokens
- API Keys

Credentials are supplied through configuration.

Authentication details remain isolated within marketplace implementations.

---

# Configuration

Example:

```text
SHOPDECK_BASE_URL=

SHOPDECK_USERNAME=

SHOPDECK_PASSWORD=

SHOPDECK_SESSION_COOKIE=

SHOPDECK_TIMEOUT=

SHOPDECK_VERIFY_SSL=
```

Credentials must never appear in source code.

---

# Synchronization History

Every synchronization produces a Synchronization Run.

Information recorded:

- Synchronization ID
- Marketplace
- Accounting Period
- Start Time
- End Time
- Status
- Reports Downloaded
- Duplicate Reports
- Imported Reports
- Failed Reports

---

# Connector Status

Possible states:

- Connected
- Authenticating
- Downloading
- Importing
- Completed
- Failed
- Authentication Failed
- Session Expired
- Duplicate Reports

---

# Error Handling

Recoverable:

- Network Timeout
- Duplicate Reports
- Temporary Server Error

Non-Recoverable:

- Invalid Credentials
- Invalid Report Format
- Missing Permissions

Every failure must provide actionable information.

---

# Security

The Connector Engine must never:

- Store plaintext passwords
- Log credentials
- Log session cookies
- Log authentication tokens

Secrets remain encrypted or environment-backed.

---

# Observability

Every synchronization records:

- Duration
- Download Size
- API Calls
- Response Codes
- Retry Count

This information supports operational monitoring.

---

# Extensibility

New marketplaces should require only:

1. New connector implementation.
2. Marketplace configuration.
3. Marketplace report mappings.

No downstream business logic should change.

---

# Success Criteria

The Connector Engine is considered complete when a user can:

1. Click **Sync ShopDeck**.
2. Authenticate automatically.
3. Download required reports.
4. Detect duplicates.
5. Store reports securely.
6. Trigger Data Ingestion automatically.
7. Complete the accounting pipeline without manual file handling.

---

# Guiding Principle

**The Connector Engine exists to eliminate manual report handling while ensuring every imported business document remains secure, traceable, deterministic, and fully auditable.**
