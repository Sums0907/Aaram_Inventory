# AARAMBOOKS INVENTORY — DATABASE AND WORKFLOW HANDOFF

## Inventory Truth
InventoryMovement is the authoritative inventory movement ledger. Historical rows must not be deleted or recalculated merely because legacy source code was retired.

## Known Movement Semantics
| Physical event | Inventory movement |
|---|---|
| PACKED | SALES_FULFILLMENT, negative quantity |
| RTO_RECEIVED | RTO_RETURN, positive quantity |
| CUSTOMER_RETURN_RECEIVED | CUSTOMER_RETURN, positive quantity |

A single external event may create multiple movement rows, one per SKU/item.

## PackerEvent
A dedicated event-level record exists so one physical event can be idempotently processed even when it produces multiple movements.

Conceptually it records:
- id
- event_id
- event_type
- order_id
- occurred_at
- received_at
- status
- payload

`event_id` is unique.

## PACKED Processing
1. Validate payload.
2. Check event_id.
3. If already processed, return ALREADY_PROCESSED.
4. Persist event.
5. Generate movement(s).
6. Commit atomically.

## Return Processing
Inventory receives only accepted physical return items, never expected return quantities.

Example:
Expected SKU-A x2, received/accepted SKU-A x1 -> MISMATCH, Inventory receives SKU-A +1.

## Transaction Requirement
Event receipt and generated InventoryMovement rows must obey the intended atomic transaction boundary. Processing failure must not leave partial inventory truth.

## Fresh Session Rule
After a write transaction commits, close the writing session and verify the durable state with a fresh session.

## Historical Data
Historical movements generated through the old reconciliation pathway remain valid historical ledger records.

## Caution
This is an architectural reference. Inspect the actual current SQLAlchemy models, schemas and migrations before modifying exact fields or relationships.
