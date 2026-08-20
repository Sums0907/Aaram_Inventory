# AARAMBOOKS INVENTORY — IMPLEMENTATION RULES FOR ANTIGRAVITY

1. Inspect current source before modifying anything.
2. Preserve Inventory Truth Engine business rules.
3. Never restore ShopDeck reconciliation as an active physical inventory source.
4. Consume explicit Packer events rather than commerce-status inference.
5. Preserve atomic transaction boundaries.
6. Verify durable writes with fresh sessions.
7. Use database-backed idempotency, not process memory.
8. Do not impose a simplistic one-fulfillment-per-order rule that blocks legitimate physical cycles.
9. For returns, replenish only accepted physical quantities.
10. Never reopen PACKED or RECONCILED solely because synchronization failed.
11. Preserve historical InventoryMovement data.
12. Golden Certification is an independent project:
`/Users/sumatidhingra/Documents/Aaram_IntegrationCertification`
13. Keep certification artifacts outside the Inventory repository root.
14. Never invent an API, field, authentication mechanism or startup command when source inspection can establish the real behavior.
