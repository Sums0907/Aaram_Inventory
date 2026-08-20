# AaramBooks Inventory

Production-grade inventory management system for Aaram Homes.

---

## Quick Start

```bash
# Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start backend
uvicorn src.app.main:app --reload --port 8080

# Start frontend
cd frontend && npm install && npm run dev
```

---

## Architecture Overview

AaramBooks follows a domain-driven design with a frozen foundation layer.

```
src/
├── foundation/          # FROZEN — Generic infrastructure (DB, config, auth, logging)
└── domains/
    ├── masters/         # Master data models (UOM, Category, Product, SKU, BOM, Supplier)
    ├── inventory/       # Inventory truth engine (movements, balances, receipts, job work)
    ├── operations/      # Sales orders, invoices, payments, settlements
    ├── accounting/      # Journal entries, ledgers, job worker accounting
    ├── data_ingestion/  # Import/Export framework + ShopDeck/Razorpay adapters
    └── connectors/      # External system connectors (ShopDeck, Razorpay)
```

See `docs/MASTER_ARCHITECTURE.md` for the full architecture.

---

## AaramBooks Master Data Import/Export Framework

The Master Data Import/Export Framework provides production-safe database initialization and master data maintenance capabilities.

### Framework Architecture

```
AaramBooks Master Data Import/Export Framework
│
│   Common Layer (src/domains/data_ingestion/services/master_data_importer.py):
│   - File parsing (Excel / CSV)
│   - Identity resolution (Exact / Partial / Ambiguous / No Match)
│   - Dry-run execution
│   - Diff generation
│   - Transaction handling
│   - Audit logging
│
├── Raw Material Master Data Import/Export Sub-Engine
│   │   Status: ✅ IMPLEMENTED — PRODUCTION CERTIFIED
│   │
│   │   Owned by: AaramBooks operations team
│   │   Entities:
│   ├── UOM
│   ├── Operational Categories (RM / PKG / CON / AST)
│   ├── Suppliers
│   ├── Raw Material Items
│   └── Bill of Materials
│
└── SKU Master Data Import/Export Sub-Engine
        Status: ⏳ FUTURE
        
        Owned by: ShopDeck Catalogue
        Entities:
        - Finished Goods categories
        - Finished Goods SKUs (from ShopDeck CSV)
        - ShopDeck taxonomy synchronization
```

### Governance Rules

See [`docs/ENTITY_IMPORT_RULE_MATRIX.md`](docs/ENTITY_IMPORT_RULE_MATRIX.md) for the complete governance rules.

Key principles:
- **EXACT MATCH → IGNORE** (idempotent)
- **PARTIAL MATCH → UPDATE** (mutable fields only)
- **NO MATCH → CREATE**
- **AMBIGUOUS MATCH → REJECT** (manual review required)
- **Dry-run is default** — explicit `--commit` required to persist

### CLI Usage

```bash
# Always dry-run first — review output before committing
python scripts/manage_imports.py \
    --entity UOM \
    --file AaramBooks_Master_Data_Import_Template.xlsx \
    --sheet UoM \
    --env staging

# Commit when satisfied with dry-run report
python scripts/manage_imports.py \
    --entity UOM \
    --file AaramBooks_Master_Data_Import_Template.xlsx \
    --sheet UoM \
    --env production \
    --commit

# Entity types: UOM | OPERATIONAL_CATEGORY | SUPPLIER | RAW_MATERIAL | BOM
```

### Import Order (Dependency Chain)

```
1. UOM                    (no dependencies)
2. OPERATIONAL_CATEGORY   (no dependencies — parents before children in file)
3. SUPPLIER               (no dependencies)
4. RAW_MATERIAL           (depends on UOM and Category)
5. BOM                    (depends on Raw Material SKUs)
```

### Certification

The framework is production certified. See [`docs/MASTER_DATA_IMPORT_CERTIFICATION_REPORT.md`](docs/MASTER_DATA_IMPORT_CERTIFICATION_REPORT.md).

25 certification tests pass covering:
- Idempotency (CERT-001)
- Partial match updates (CERT-002)
- Ambiguous match rejection (CERT-003)
- Identity immutability (CERT-004, CERT-005, CERT-010)
- Category root protection (CERT-006)
- Hierarchy governance (CERT-007, CERT-008, CERT-009)
- BOM content versioning (CERT-012, CERT-013)
- Dry-run safety (CERT-016)
- Transaction safety (CERT-017)
- Golden Migration Test — two independent databases given identical input produce identical state (CERT-020)

---

## Packer Integration

AaramBooks receives webhook events from Aaram Packer and translates them into inventory movements.

**Endpoint:** `POST /api/v1/internal/webhooks/packer/events`

Accepted events: `PACKED`, `RTO_RECEIVED`, `CUSTOMER_RETURN_RECEIVED`

Integration is certified — see `docs/GOLDEN_CERTIFICATION_READINESS.md`.

---

## Database

SQLite for development. PostgreSQL for staging/production.

```bash
# Run migrations
alembic upgrade head

# Check current version
alembic current
```

Environment variables required: `DATABASE_URL`, `DATABASE_ENV`, `SHOPDECK_SALES_WAREHOUSE_CODE`

---

## Testing

```bash
# Full test suite
PYTHONPATH=. venv/bin/pytest tests/ -v

# Master Data Import certification only
PYTHONPATH=. venv/bin/pytest tests/data_import/ -v

# Packer integration certification
PYTHONPATH=. venv/bin/pytest tests/inventory/ -v
```

---

## Key Documentation

| Document | Purpose |
|:---------|:--------|
| [`AI_HANDOFF.md`](AI_HANDOFF.md) | AI agent handoff — current state and next steps |
| [`docs/MASTER_ARCHITECTURE.md`](docs/MASTER_ARCHITECTURE.md) | Full system architecture |
| [`docs/MASTER_DATA_SUB_ENGINE_ARCHITECTURE.md`](docs/MASTER_DATA_SUB_ENGINE_ARCHITECTURE.md) | Import/Export framework design |
| [`docs/ENTITY_IMPORT_RULE_MATRIX.md`](docs/ENTITY_IMPORT_RULE_MATRIX.md) | Governance rules for all importers |
| [`docs/IMPORTER_REFACTOR_PLAN.md`](docs/IMPORTER_REFACTOR_PLAN.md) | Planned refactor to sub-engine structure |
| [`docs/RAW_MATERIAL_EXPORT_ENGINE_PLAN.md`](docs/RAW_MATERIAL_EXPORT_ENGINE_PLAN.md) | Export engine design |
| [`docs/MASTER_DATA_IMPORT_CERTIFICATION_REPORT.md`](docs/MASTER_DATA_IMPORT_CERTIFICATION_REPORT.md) | Certification results |
| [`docs/INVENTORY_CERTIFIED_BASELINE.md`](docs/INVENTORY_CERTIFIED_BASELINE.md) | Inventory truth engine baseline |
| [`docs/CATEGORY_MIGRATION_ANALYSIS.md`](docs/CATEGORY_MIGRATION_ANALYSIS.md) | Dev DB category analysis |

---

## Foundation Layer

The `src/foundation/` layer is **FROZEN**. Do not modify without explicit approval. It provides generic infrastructure — database sessions, configuration, authentication, enums, logging — that all domains depend on.
