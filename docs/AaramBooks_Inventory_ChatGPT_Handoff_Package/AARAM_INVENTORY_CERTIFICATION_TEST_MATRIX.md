# AARAMBOOKS INVENTORY — GOLDEN CERTIFICATION TEST MATRIX

Certification must run from `/Users/sumatidhingra/Documents/Aaram_IntegrationCertification` and exercise the real applications.

## CERT-001 PACKED Happy Path
Actual Packer packing -> outbox -> dispatcher -> Inventory receiver -> PackerEvent -> SALES_FULFILLMENT. Verify SKU, quantity and durable persistence.

## CERT-002 PACKED Inventory Outage
Inventory unavailable. Verify order remains PACKED, outbox remains pending, event identity/payload remain unchanged, recovery eventually delivers.

## CERT-003 PACKED Duplicate
Same event ID/payload delivered repeatedly. Verify one logical event and one movement set.

## CERT-004 Concurrent Duplicate
Same event concurrently delivered. Verify database-backed idempotency prevents duplicate ledger rows.

## CERT-005 RTO MATCH
Actual Packer reconciliation. Verify accepted items produce RTO_RETURN.

## CERT-006 RTO Partial MISMATCH
Example expected SKU-A x2, accepted SKU-A x1. Verify MISMATCH but only +1 reaches Inventory.

## CERT-007 Clubbed Partial Recovery
Expected five items, only three valid accepted. Verify only those three enter Inventory.

## CERT-008 Damaged Exclusion
Verify DAMAGED items do not enter available stock.

## CERT-009 Wrong SKU Exclusion
Verify WRONG_SKU is excluded.

## CERT-010 Unknown/Rejected Exclusion
Verify UNKNOWN_ITEM and REJECTED are excluded.

## CERT-011 Zero Quantity
Verify zero accepted quantity is omitted.

## CERT-012 Return Inventory Outage
Verify reconciliation remains physically reconciled, outbox stays pending and later recovers.

## CERT-013 Return 4xx
Verify permanent failure becomes NEEDS_REVIEW/FAILED and is not automatically retried.

## CERT-014 Return Duplicate
Verify duplicate return event cannot create duplicate movement.

## CERT-015 Atomic Rollback
Inject processing failure. Verify no partial event/movement state remains.

## CERT-016 Fresh Session Persistence
Commit, close writer, reopen fresh session and verify durable state.

## CERT-017 Restart Recovery
Restart with pending events. Verify dispatcher resumes without duplication.

## CERT-018 ShopDeck Isolation
Run legacy reconciliation/report path and verify zero new Inventory movements.

## CERT-019 Historical Preservation
Verify architectural cleanup does not alter historical movements.

## CERT-020 Ledger Reconciliation
Compare controlled physical events with Packer events and InventoryMovement effects. A unit test alone is insufficient evidence.
