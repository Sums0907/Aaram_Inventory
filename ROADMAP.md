# AaramBooks Product Roadmap

A high-level view of the product evolution for AaramBooks, transitioning from E-commerce Accounting Automation towards a full-scale Inventory Intelligence platform.

## v0.2.0: Core Infrastructure
✅ **Foundation:** Base architecture, dependency injection, exception handling, utilities.
✅ **Masters:** SKUs, Companies, Categories, Warehouses, UOMs.

## v0.3.0: E-commerce Connectivity
✅ **Data Ingestion:** Extensible ingestion pipeline (Jobs, Files, Records, Summaries) with specific parsers for ShopDeck Orders, Tax Reports, COD Settlements, and Razorpay Payments.

## v0.4.0: Canonical Staging
🚧 **Operations:** The transactional heart. Transforming raw ingested records into structured Business Objects (`SalesOrder`, `TaxInvoice`, `Payment`, `Settlement`, `Refund`) and committing them to the operational database.

## v0.5.0: Reconciliation
⏳ **Matching:** The intelligence layer. Establishing relationships between disparate commerce objects (e.g., matching a Razorpay `Payment` to a ShopDeck `SalesOrder`, or a COD `Settlement` to its underlying payments).

## v0.6.0: Stock Control
⏳ **Inventory:** Using the matched Operations data to build inventory capabilities (Reservations, Stock Movement, Warehouse Stock, Inventory Reports) based on real business events.

## v0.7.0: Financials
⏳ **Accounting:** Consuming the reconciled Operations and Inventory events to automatically generate accurate General Ledger journals (Revenue, Tax Liability, Fees, Accounts Receivable).

## v0.8.0: The Vyapar Bridge
⏳ **Vyapar Export:** Generating Vyapar-compatible exports to completely automate external accounting synchronization without duplicating efforts.

## v0.9.0: Business Insights
⏳ **Reports:** High-level dashboards, analytics, and business intelligence built on top of the canonical Operational and Accounting ledgers.

## v1.0.0: Go Live
🚀 **Production:** Stable, automated, and ready for daily operational use.
