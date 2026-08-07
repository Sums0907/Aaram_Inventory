# AaramBooks Version 1 - Release Candidate 1 (RC1)

## Overview
AaramBooks Version 1 RC1 marks the completion of the core data ingestion, operations matching, and accounting lifecycle features. The architecture is frozen and optimized for high-volume enterprise e-commerce reconciliation.

## Key Features
- **Data Ingestion**: High-throughput file upload, background parsing, and database batch committing.
- **Operations Matching Engine**: Advanced matching heuristics connecting e-commerce orders (ShopDeck) to payment gateways (Razorpay).
- **Double Entry Accounting**: Automated ledger generation mapping e-commerce events (Sales, Returns, Settlements, Gateway Fees) to compliant debit/credit journal entries.
- **Vyapar Export**: Native export endpoints generating accounting software (Vyapar) compliant ledger imports.
- **Robustness**: 100% End-to-End Validation pipeline matching the Golden Dataset, sub-10ms API response times via strategic indexing, and resilient UI error boundaries.

## Known Limitations
- V1 does not yet support multi-tenant scaling natively through the application layer, though the DB schema accommodates it.
- Direct live API integrations to ShopDeck/Razorpay are slated for V2.

## Deployment Instructions
See `docker-compose.prod.yml` for the standard production deployment topology using PostgreSQL and Uvicorn workers.

---

# AaramBooks Version 1 - Release Candidate 2 (RC2)

## Overview
AaramBooks Version 1 RC2 expands the Inventory Truth Engine to fully understand and process the major real-world operational events that occur throughout the physical lifecycle of inventory.

## Key Features
- **Event-Driven Operational Inventory**: Inventory balances are no longer just updated via sales. We introduced deterministic tracking of `PURCHASE_RECEIPT`, `PURCHASE_RETURN`, `CUSTOMER_RETURN`, `RTO_RETURN`, `MANUAL_ADJUSTMENT`, and `STOCK_COUNT_ADJUSTMENT`.
- **Business-Oriented APIs**: Low-level database manipulation is eliminated. All operational inventory events run through specific API endpoints (e.g., `POST /api/v1/inventory/movements/purchase-receipts`).
- **Auditability & Traceability**: Each manual stock correction and physical count disparity generates immutable `InventoryMovement` records.
- **Enhanced Exceptions & Confidence**: Invalid combinations (such as negative stock remaining after an adjustment) are natively routed into the Inventory Exception system, preventing silent errors.

## Known Limitations
- Warehouse Transfers, Bin Locations, and Multi-Warehouse setups are slated for RC3.
- Financial Valuation, Purchase Accounting, and COGS calculations are out of scope and reserved for future updates to the Accounting Engine.

---

# AaramBooks Version 1 - Release Candidate 3 (RC3)

## Overview
AaramBooks Version 1 RC3 introduces **Inventory Intelligence**, transforming the raw data of the Inventory Truth Engine into a business-facing operational command center.

## Key Features
- **Inventory Dashboard**: A completely redesigned React frontend interface displaying executive KPIs such as Tracked SKUs, Current Stock, Average Confidence, and Total Negative Inventory.
- **Exceptions Workbench**: Actionable operational triage UI. Automatically surfaces problematic stock levels (like mathematically impossible negative inventory) for resolution rather than just reporting them.
- **SKU Intelligence Directory**: A search-enabled directory for quickly browsing inventory.
- **Interactive Ledger Drill-down**: The ability to click into any SKU to view the full chronological timeline of its inventory movements alongside its exact confidence signals.

## Known Limitations
- Multi-Warehouse Support, Warehouse Transfers, and Bin Locations are deferred to RC4.
- Forecasting, Reservations, and Quality Control are slated for future releases.
