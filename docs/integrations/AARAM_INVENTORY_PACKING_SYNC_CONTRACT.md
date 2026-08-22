# Aaram Inventory ↔ Aaram Packing Sync Contract

## 1. Ownership Boundaries
- **Aaram Inventory (Master)**: Owns SKU Master Data, Identity Resolution (Importing), Inventory Ledger, Movement Authority, and Global Stock Balance.
- **Aaram Packing (Client)**: Owns physical packing execution, Barcode Scanning, Outbound fulfillment workflows, RTO, and Return Receiving logic.

## 2. Event Contracts: Inventory → Packer (Outbound)

The Inventory system is responsible for pushing canonical, operational SKU projections to the Packer app. 
**No internal logic (import history, resolution algorithms, duplicate handling, accounting, suppliers) is exposed to the Packer.**

### A. SKU Events
Only SKUs explicitly marked as `FINISHED_GOODS` will be pushed. Raw materials are excluded.

**Topic / Endpoints**: `/webhooks/packer/sku-sync`

#### 1. `SKU_CREATED` / `SKU_UPDATED`
Fired when a new Finished Good SKU is created or an existing one is updated in the Inventory Master.
```json
{
  "event_id": "evt_abc123",
  "event_type": "SKU_UPDATED",
  "timestamp": "2026-08-22T10:00:00Z",
  "payload": {
    "inventory_sku_id": "uuid-1234-5678",
    "sku_code": "TSHIRT-BLK-L",
    "barcode": "8901234567890",
    "name": "Men's Black T-Shirt",
    "category": "Apparel",
    "variant": "Large",
    "size": "L",
    "color": "Black",
    "status": "ACTIVE"
  }
}
```

#### 2. `SKU_DEACTIVATED`
```json
{
  "event_id": "evt_abc124",
  "event_type": "SKU_DEACTIVATED",
  "timestamp": "2026-08-22T10:05:00Z",
  "payload": {
    "inventory_sku_id": "uuid-1234-5678"
  }
}
```

#### 3. `SKU_MASTER_SNAPSHOT_SYNC`
Used during the Daily Reconciliation Job to transmit a bulk snapshot of all active Finished Goods SKUs.
```json
{
  "event_id": "evt_abc125",
  "event_type": "SKU_MASTER_SNAPSHOT_SYNC",
  "timestamp": "2026-08-22T00:00:00Z",
  "batch_id": "batch_888",
  "payload": [
    { /* Canonical SKU Object */ },
    { /* Canonical SKU Object */ }
  ]
}
```

### B. Stock Balance Events
The Inventory system calculates movements. The Packer system ONLY receives the resulting balance. Raw movements are never exposed.

#### `STOCK_BALANCE_CHANGED`
Fired when the global available quantity for a SKU changes (e.g. GRN received, manual adjustment).
```json
{
  "event_id": "evt_abc126",
  "event_type": "STOCK_BALANCE_CHANGED",
  "timestamp": "2026-08-22T10:15:00Z",
  "payload": {
    "inventory_sku_id": "uuid-1234-5678",
    "available_qty": 145,
    "timestamp": "2026-08-22T10:14:59Z"
  }
}
```

## 3. Existing Event Contracts: Packer → Inventory (Inbound Review)

The existing queue-based synchronization forwards fulfillment execution states from Packer to Inventory.
**Current Validated Events:**
- `SALE` / `PACKING_COMPLETION`: Deducts stock.
- `RTO` / `RETURN`: Restores stock.

**Integrity Verification:**
The Inventory system strictly remains the Movement Authority. It receives these events as "requests" or "operational facts", but the Inventory ledger ultimately processes the ledger delta and commits the transaction.

## 4. Failure Handling & Retry Strategy
- **Retry Mechanism**: Exponential backoff (e.g., 5s, 30s, 5m, 1h) for any non-200 webhook response.
- **Idempotency**: All webhooks include a unique `event_id`. The receiving system (Packer or Inventory) MUST store processed `event_id`s in an idempotency key table for 7 days to silently drop duplicate deliveries.
- **Dead Letter Queue (DLQ)**: Events failing after 5 retries are routed to a DLQ for manual admin inspection.
