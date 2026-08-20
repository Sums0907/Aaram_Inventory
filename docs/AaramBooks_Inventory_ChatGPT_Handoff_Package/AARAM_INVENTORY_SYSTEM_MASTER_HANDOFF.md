# AARAMBOOKS INVENTORY SYSTEM — MASTER HANDOFF

## Purpose
This is the primary continuity handoff for future ChatGPT/Antigravity sessions working on AaramBooks Inventory. Treat it as the current architecture baseline. Do not redesign completed decisions unless explicitly requested.

## System Role
AaramBooks Inventory is the Inventory Truth Engine. It maintains the authoritative inventory movement ledger and converts explicit physical warehouse events into inventory movements.

Aaram Packer is the physical warehouse event authority.

ShopDeck Order Reconciliation is no longer an active inventory movement source.

## Final Architecture
```text
ShopDeck
  |
Commercial order identity
  |
  X  No physical-inventory inference
  |
Aaram Packer
  |
Explicit physical warehouse events
  |
AaramBooks Inventory API
  |
PackerEvent / event receipt
  |
Inventory Movement Service
  |
Inventory Movement Ledger
```

## Completed Integration Areas

### PACKED
```text
Packer physically packs
  -> PACKED state
  -> durable outbox
  -> dispatcher
  -> Inventory webhook
  -> PackerEvent
  -> SALES_FULFILLMENT
```

### RTO / Customer Return
```text
Return received
  -> physical item/quantity reconciliation
  -> MATCH or MISMATCH
  -> accepted inventory-eligible items
  -> durable return outbox
  -> dispatcher
  -> Inventory webhook
  -> RTO_RETURN / CUSTOMER_RETURN
```

## Permanent Invariants
1. Packer is the physical event authority.
2. Inventory does not infer physical movements from commerce status.
3. ShopDeck reconciliation cannot create new inventory movements.
4. Historical InventoryMovement rows remain untouched.
5. PACKED remains PACKED when Inventory is unavailable.
6. Reconciled RTO/Return does not reopen because synchronization fails.
7. Event IDs are immutable.
8. Retries reuse the same event ID.
9. Retries reuse the exact persisted payload.
10. Duplicate events cannot create duplicate movements.
11. Return inventory contains only accepted physical quantities.
12. DAMAGED, WRONG_SKU, UNKNOWN_ITEM, REJECTED and zero-quantity items are excluded from normal available inventory.
13. Event processing is transactional.
14. Important persistence tests verify state using a fresh session.

## ShopDeck Status
ShopDeck Order Reconciliation is retired as an inventory ingestion mechanism.

The ShopDeck connector is archived/deprecated rather than deleted.

No new Inventory functionality should be built on the archived connector.

## Current Next Phase
Both Packer outbound and Inventory receiver implementations exist for PACKED and RTO/Return flows.

The next major activity is independent end-to-end Golden Certification using:
`/Users/sumatidhingra/Documents/Aaram_IntegrationCertification`

## Continuation Instruction
Treat this document as the architecture baseline. Continue from integration certification, production hardening and operational readiness.
