# AARAMBOOKS INVENTORY — ARCHITECTURAL DECISION LOG

## 1. Packer is Physical Truth
Warehouse events are physical realities, so Packer is the source of explicit physical inventory events.

## 2. ShopDeck Reconciliation Retired
Commerce reports are a proxy and should not generate physical inventory movements.

## 3. ShopDeck Connector Archived, Not Deleted
Preserve possible future integration capability without making Inventory dependent on it.

## 4. PACKED Is Permanent
Inventory API failure cannot undo a physical packing action.

## 5. Durable Outbox
Physical state change and outbound integration event must be persisted atomically.

## 6. Event-Level Idempotency
One physical event can create multiple movement rows, so idempotency is attached to the event.

## 7. Different Event IDs Can Represent Legitimate Cycles
Do not globally enforce one SALES_FULFILLMENT per order forever.

## 8. MATCH and MISMATCH Both Transmit
A mismatch can still recover valid physical stock.

## 9. Accepted Physical Return Quantity Is Authoritative
Expected-side quantities do not replenish inventory.

## 10. Damaged Excluded
Damaged stock is excluded from normal available inventory until a dedicated quarantine/damaged model exists.

## 11. Retry Semantics
2xx = delivered; 5xx/network/timeout = retry; 4xx = needs review/no automatic retry.

## 12. Fresh Session Persistence
Durability must be verified independently of the writing ORM session.

## 13. Independent Golden Certification
Cross-system certification belongs in a separate project rather than either production source tree.
