# Aaram Inventory ↔ Aaram Packing Implementation Plan

## Overview
This document outlines the architectural plan for implementing the robust, bi-directional event-driven sync between Aaram Inventory (Master) and Aaram Packing (Client). No code changes have been executed; this serves as the definitive roadmap.

---

## Phase 1: Canonical Outbound Projections (Inventory)

### 1. Identify Target Audience
- Update `ProductSKUImporter` and Database triggers to isolate `FINISHED_GOODS`.
- Ensure raw materials and internal BOM parts are explicitly filtered out from outbound queues.

### 2. Canonical Payload Mapper
- Build a serializer in Aaram Inventory that strips all internal import logic, supplier logic, and cost accounting fields.
- Map the SKU to the flat, operational JSON schema defined in the Sync Contract (containing only `inventory_sku_id`, `barcode`, `sku_code`, `name`, `category`, `variant`, `status`).

---

## Phase 2: Core Event Engine (Inventory)

### 1. Publish SKU Lifecycle Events
- **Hook Location**: SQLAlchemy `after_insert`, `after_update`, or Application Service Layer logic for SKUs.
- **Action**: Whenever a Finished Good is created, updated, or deactivated, push the canonical payload to the `inventory_outbound_events` table (Outbox Pattern).

### 2. Publish Stock Balance Events
- **Hook Location**: Ledger transaction commits.
- **Rule**: Do NOT broadcast `InventoryMovementModel` details. Instead, on successful commit, query the newly calculated available balance for the SKU.
- **Action**: Push a `STOCK_BALANCE_CHANGED` event containing strictly the `inventory_sku_id`, new `available_qty`, and `timestamp` to the outbox.

### 3. Outbox Publisher Daemon
- Build a background worker (or leverage Celery/Redis) to poll the `inventory_outbound_events` table and fire Webhooks to the Packer API.
- Implement exponential backoff and idempotency keys (`event_id`).

---

## Phase 3: Daily Reconciliation Job (Inventory)

### 1. Full Snapshot Generation
- Schedule a CRON job (e.g., 03:00 AM Daily).
- Query all active Finished Good SKUs.
- Chunk the response into manageable batches (e.g., 1000 SKUs per batch).

### 2. Reconciliation Execution
- Push the batches to Packer via the `SKU_MASTER_SNAPSHOT_SYNC` event.
- This acts as a self-healing mechanism to resolve any dropped webhooks or desynchronized state over the last 24 hours.

---

## Phase 4: Validating the Inbound Engine (Packer -> Inventory)

### 1. Existing Infrastructure Review
- The current packing webhook flow (`handle_packer_event`) correctly processes `SALE` and `RETURN` payloads.
- **Architectural Validation**: Inventory remains the undisputed movement authority. The Packer app merely signals the operational execution, while Inventory calculates the ledger impact.

### 2. Enhancements Required
- Integrate the missing **Dynamic Warehouse Context** (as planned previously) into these inbound payloads so the ledger knows exactly which physical location to deduct stock from.
- Enforce Idempotency on `event_id` to prevent double-deduction in case the Packer Backend retries a webhook.

---

## Execution Constraints
- No migrations or code changes are to be made until explicit user approval is granted to begin Phase 1.
