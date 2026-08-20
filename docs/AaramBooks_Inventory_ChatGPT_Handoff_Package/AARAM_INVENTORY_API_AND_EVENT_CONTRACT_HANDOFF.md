# AARAMBOOKS INVENTORY — API AND EVENT CONTRACT REFERENCE

## Endpoint
`POST /api/internal/webhooks/packer/events`

## Payload
```json
{
  "event_id": "RTO-1042",
  "event_type": "RTO_RECEIVED",
  "occurred_at": "2026-08-17T10:30:00Z",
  "order_id": "SHOPDECK-ORD-999",
  "awb": "REVERSE-AWB-456",
  "items": [
    {"sku": "SKU-ABC", "quantity": 1}
  ]
}
```

## Field Semantics
- `event_id`: immutable external event/idempotency identifier.
- `event_type`: PACKED, RTO_RECEIVED or CUSTOMER_RETURN_RECEIVED.
- `occurred_at`: actual physical event time.
- `order_id`: stable commercial identity.
- `awb`: logistics identifier.
- `items`: exact physical quantities represented by the event.

## SKU Rule
No fuzzy SKU matching or conversion should be introduced at this boundary. Packer sends canonical SKU values.

## Quantity Rule
Payload quantities are positive. Movement direction is determined by event type.

## Idempotency
First delivery -> PROCESSED. Repeated same event -> ALREADY_PROCESSED. No duplicate movement generation.

## Contract Changes
Coordinate changes across both projects. Do not silently alter event ID semantics, item meaning, event types, movement semantics or retry behavior.
