# Aaram Inventory ↔ Packing Integration Implementation Plan

## Current State
- **Inventory** is the Source of Truth for SKUs, Ledger, and Movements. It lacks an outbound synchronization mechanism.
- **Packer** executes operations and pushes outbound webhooks (`inventory_client.py` -> `/webhooks/packer/events`). It currently relies on static/isolated SKU lists and lacks dynamic updates from Inventory.
- **Database Sharing**: None (which is good). Communication is purely via HTTP REST, but it's currently unidirectional (Packer -> Inventory).

## Target State
We will implement a robust, bi-directional, event-driven sync using the Outbox pattern.
- **Inventory** will push canonical operational projections (Finished Goods only) via `inventory_outbound_events`.
- **Packer** will consume these events and maintain read-only projections (`packer_sku_projection`, `packer_stock_projection`) without claiming business ownership.
- **Resilience**: Idempotency checks on both sides, exponential retries, and a daily scheduled reconciliation job (Master Snapshot Sync).
- **Security**: Existing AaramIdentity PBAC mechanisms will enforce service-to-service authorization (e.g. `INVENTORY_MASTER_DATA_EXPORT` and `INVENTORY_ACTIVITY_VIEW`).

## Database Changes
### Inventory System
1. `inventory_outbound_events`: Outbox table for queueing outgoing webhooks (status, retry counts).

### Packer System
1. `packer_sku_projection`: Flat read-model storing canonical SKU details.
2. `packer_stock_projection`: Read-model storing the most recent `available_qty`.
3. `inventory_sync_events`: Idempotency and audit table to track processed incoming `event_id`s.

## Files Impacted
### Inventory System
- `src/domains/inventory/models/outbox.py` [NEW]
- `src/domains/inventory/services/outbound_event_publisher.py` [NEW]
- `src/domains/data_ingestion/services/product_sku_importer.py` [MODIFY]
- `src/domains/inventory/services/movement_service.py` [MODIFY]
- `src/domains/inventory/tasks/daily_reconciliation.py` [NEW]

### Packer System
- `backend/app/models/projection.py` [NEW]
- `backend/app/api/inventory_webhook.py` [NEW]
- `backend/app/services/inventory_event_handler.py` [NEW]

## Event Contracts
| Event Type | Payload Attributes |
|---|---|
| `SKU_CREATED` / `SKU_UPDATED` | `inventory_sku_id`, `sku_code`, `barcode`, `name`, `category`, `variant`, `size`, `color`, `status` |
| `SKU_DEACTIVATED` | `inventory_sku_id` |
| `STOCK_BALANCE_CHANGED` | `inventory_sku_id`, `available_qty`, `timestamp` |
| `SKU_MASTER_SNAPSHOT_SYNC` | Array of Canonical SKU Projections |
