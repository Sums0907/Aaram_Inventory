# AARAMBOOKS INVENTORY — DATABASE ENTITY REFERENCE

## InventoryMovement
Authoritative inventory ledger record.

Known movement semantics:
- SALES_FULFILLMENT = stock leaving inventory.
- RTO_RETURN = accepted RTO stock entering inventory.
- CUSTOMER_RETURN = accepted customer-return stock entering inventory.

## PackerEvent
External physical event receipt record used for event-level idempotency and auditability.

Conceptual fields established in the integration design:
- id
- event_id
- event_type
- order_id
- occurred_at
- received_at
- status
- payload

One PackerEvent can create multiple InventoryMovement rows.

## SalesOrder
Commercial order identity remains useful independently of legacy reconciliation. `order_id` is the stable commercial identity used by the integration.

## Legacy Fields
Some SalesOrder lifecycle fields may have originated in Phase C/D reconciliation. Do not remove them without a current-code dependency audit.

## Rule
This reference is not permission to assume exact schema details. Inspect the current repository before changing entities, migrations or relationships.
