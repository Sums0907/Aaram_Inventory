# AaramBooks Inventory Outbound Sync Implementation Report

## Architecture Summary
The outbound synchronization architecture strictly enforces AaramBooks Inventory as the definitive Source of Truth. The integration uses the **Transactional Outbox Pattern** to broadcast state changes across the network, completely avoiding database sharing.

### 1. Database Additions
- **Table**: `inventory_outbound_events`
- **Model**: `src/domains/inventory/models/outbox.py (InventoryOutboundEventModel)`
- **Purpose**: A persistent queue enforcing atomicity. Events are stored in the same database transaction as the business operation. 

### 2. Event Producers
1. **SKU Master Synchronization (`Phase 2`)**:
   - Location: `src/domains/data_ingestion/services/product_sku_importer.py`
   - Trigger: Emits `SKU_CREATED`, `SKU_UPDATED`, or `SKU_DEACTIVATED` upon a successful CSV ingest commit.
   - Filter: Only generates events for `ItemType.FINISHED_GOODS`.
2. **Stock Quantity Synchronization (`Phase 3`)**:
   - Location: `src/domains/inventory/services/balance_calculator.py`
   - Trigger: Emits `STOCK_BALANCE_CHANGED` after the Confidence Engine and movement algorithms establish the absolute projected quantity. Ledger mechanics remain fully obfuscated from the consumer.
3. **Daily Reconciliation (`Phase 8`)**:
   - Location: `src/domains/inventory/tasks/daily_reconciliation.py`
   - Trigger: Scheduled background task that aggregates all Active Finished Goods into a single bulk `SKU_MASTER_SNAPSHOT_SYNC` payload for consumer hydration.

### 3. Event Dispatcher
- **Service**: `src/domains/inventory/services/outbound_event_publisher.py`
- **Responsibilities**: Polling the `PENDING` queue, translating to HTTP Webhooks, and executing exponential backoff retries. Unrecoverable webhooks (5+ failures) are flagged as `DEAD_LETTER`.
- **Concurrency**: Utilizes a `with_for_update(skip_locked=True)` database lock to ensure multi-worker safety across the Uvicorn deployment.
- **Security (`Phase 9`)**: Injects `PACKER_API_TOKEN` dynamically to adhere to AaramIdentity PBAC mechanisms.

## Next Steps / Operations
- **(COMPLETED)** The `OutboundEventDispatcherService` is hooked natively into the FastAPI background task runner via `src/app/lifespan.py` to seamlessly auto-schedule dispatcher loops (every 30s) and reconciliation jobs (every 24h).
- Execute the `daily_reconciliation.py` to seed the Packer infrastructure initially.
