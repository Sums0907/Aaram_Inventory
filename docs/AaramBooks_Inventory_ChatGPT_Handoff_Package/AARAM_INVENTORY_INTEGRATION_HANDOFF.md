# AARAMBOOKS INVENTORY — PACKER INTEGRATION HANDOFF

## Roles
- Aaram Packer = physical warehouse event authority.
- AaramBooks Inventory = inventory truth processor.

## Receiver
`POST /api/internal/webhooks/packer/events`

## Common Contract
```json
{
  "event_id": "immutable-event-id",
  "event_type": "PACKED",
  "occurred_at": "2026-08-17T10:30:00Z",
  "order_id": "SHOPDECK-ORD-999",
  "awb": "LOGISTICS-AWB",
  "items": [
    {"sku": "SKU-ABC", "quantity": 1}
  ]
}
```

## Event Types
- PACKED
- RTO_RECEIVED
- CUSTOMER_RETURN_RECEIVED

## Event ID
Packer generates an immutable event ID. Every retry is the same physical event and therefore uses the same event ID.

## PACKED
Packer sends exact canonical SKU and quantity packed. Inventory creates SALES_FULFILLMENT with negative quantity.

## RTO / Customer Return
Packer manually reconciles every returned item and quantity. Both MATCH and MISMATCH can transmit. Inventory receives only accepted, inventory-eligible physical quantities.

## Excluded
- DAMAGED
- WRONG_SKU
- UNKNOWN_ITEM
- REJECTED
- missing quantities
- zero quantity

## Delivery Semantics
| Response | Packer behavior |
|---|---|
| 2xx | DELIVERED |
| ALREADY_PROCESSED | DELIVERED |
| 5xx | retry indefinitely |
| network failure / timeout | retry indefinitely |
| 4xx | NEEDS_REVIEW / FAILED; no automatic retry |

## Authentication
The design remains extensible. Earlier implementation did not hard-code production authentication as absent. Future authentication must be coordinated between both projects and the deployment environment.
