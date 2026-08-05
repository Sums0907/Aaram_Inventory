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
