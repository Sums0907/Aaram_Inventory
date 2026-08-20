# RTO / Return API Contract Design

This document establishes the exact data contract and behavioral boundary between the **Aaram Packer App** and the **AaramBooks Inventory Truth Engine** for RTOs and Customer Returns.

## Core Architectural Principle
> **Every RTO/Customer Return is manually reconciled by the Packer at item and quantity level. Once reconciliation is complete, both MATCH and MISMATCH/REJECTED returns transmit an Inventory event. The event contains only valid, inventory-eligible items and quantities physically accepted by the Packer. Missing, rejected, wrong-SKU, damaged, and otherwise non-accepted quantities are excluded from the Inventory event.**

## API Contract Decisions

### 1. Exact `rto_return_orders` fields to expose
The Packer will use these internal fields to build the event payload:
- `id` (Packer's primary key for the RTO)
- `order_id` (The external business identity, e.g., "SHOPDECK-ORD-999")
- `reverse_awb` (The tracking number for the return leg)
- `type` (`RTO` or `CUSTOMER_RETURN`)
- `reconciled_at` (When the physical scan was completed)

### 2. Exact `rto_return_received_items` fields to expose
The event will ONLY include items that are KNOWN, ACCEPTED, and INVENTORY-ELIGIBLE:
- `sku_id` (The identified product code)
- `received_qty` (The actual accepted counted quantity)

### 3. How SKU is represented
SKUs will be represented as plain strings (`"sku": "SKU-ABC"`) mapping exactly to the `sku_id` from `rto_return_received_items`.

### 4. How quantity is represented
Quantities will be strictly positive integers (`"quantity": 1`), mapping to `received_qty`. Any SKU with an accepted quantity of 0 is omitted entirely.

### 5. What status means reconciliation is complete
In the Packer App, an event is ready to be sent ONLY when:
- `status == 'RECONCILED'`

### 6. Whether `MATCH` is the only state eligible to notify Inventory
**Decision:** NO. Both `MATCH` and `MISMATCH` / `REJECTED` package states are eligible to notify Inventory. 
The package-level status just indicates if the return matched the original order. What matters to Inventory is the **accepted items**. Inventory will process whatever valid stock was actually recovered, even if it's only a partial return.

### 7. Whether a reconciled event can ever be corrected/reopened
**Decision:** NO.
Once an RTO is marked `RECONCILED` and successfully transmitted to Inventory, it becomes immutable in the Packer App. Any physical corrections later discovered must be handled via manual inventory adjustment in AaramBooks, not by re-opening the RTO.

### 8 & 9. Reliability: What if Inventory is down, and should Packer retry indefinitely?
**Decision:** Webhook delivery must distinguish between retryable and permanent failures:
- **HTTP 2xx**: DELIVERED. Stop retrying.
- **Network failure / timeout / HTTP 5xx**: PENDING. Retry indefinitely with exponential backoff.
- **HTTP 4xx**: FAILED / NEEDS_REVIEW. Do NOT retry. The payload was rejected (e.g. invalid SKU). Retain the payload in a durable outbox for manual investigation.

### 10. Does Inventory need `rto_return_order_id` for audit/idempotency?
**Decision:** YES.
To ensure idempotency and traceability, the webhook payload will include the Packer's internal RTO ID as the `event_id` (e.g., `event_id: "RTO-1042"`). One Packer return record results in exactly ONE logical inbound event to Inventory.

### 11. Damaged Items Handling
**Decision:** EXCLUDE. 
Physically received but damaged items are **not** eligible for normal available inventory. The Packer App will retain the damaged item record for audit purposes, but it will be stripped from the `items[]` array in the webhook sent to AaramBooks. (If AaramBooks later supports explicit damaged/quarantine locations, this logic can be extended).

---

## Final Webhook Payload Schema

Based on the decisions above, here is the final proposed schema that AaramBooks will expect at `POST /api/v1/internal/webhooks/packer/events`.

### For an RTO:
```json
{
  "event_id": "RTO-1042",
  "event_type": "RTO_RECEIVED",
  "occurred_at": "2026-08-17T10:30:00Z",
  "order_id": "SHOPDECK-ORD-999",
  "awb": "REVERSE-AWB-456",
  "items": [
    {
      "sku": "SKU-ABC",
      "quantity": 1
    }
  ]
}
```

### For a Customer Return:
```json
{
  "event_id": "RET-1043",
  "event_type": "CUSTOMER_RETURN_RECEIVED",
  "occurred_at": "2026-08-17T10:30:00Z",
  "order_id": "SHOPDECK-ORD-999",
  "awb": "REVERSE-AWB-789",
  "items": [
    {
      "sku": "SKU-ABC",
      "quantity": 1
    }
  ]
}
```

> **NOTE:** The `items[]` array contains ONLY physically accepted, inventory-eligible quantities. Missing items, extra wrong SKUs, `UNKNOWN_ITEM`s, and `DAMAGED` items are stripped out by the Packer App before constructing this payload.
