# AaramInventory Context Exposure Module (CEM)

## Overview

The Context Exposure Module (CEM) is the **AaramInventory-side exposure boundary** that implements the canonical **Stage F Brain ↔ Business-System Context Capability Protocol**. 

Its sole responsibility is to receive strictly formatted, generic capability requests from the AaramBooks Brain Core (specifically the Context Aggregation Engine) and map them to physical, existing AaramInventory business services to return opaque evidence data.

**Crucially, the CEM is NOT an intelligence domain.** It performs:
- **ZERO** semantic reasoning
- **ZERO** Natural Language Processing (NLP)
- **ZERO** intelligence planning
- **ZERO** arbitrary database querying

The intelligence, NLP, and cognitive planning remain entirely within the Brain Core layer (in the `aarambooks` repository). The CEM simply acts as a blind, secure dispatcher that translates agreed-upon capability URNs into explicit internal API calls.

---

## Architecture

The CEM is implemented in the `src/domains/context` package to ensure complete isolation from core inventory business logic, maintaining the frozen integrity of the Foundation layer.

### 1. Contracts (`contracts.py`)
AaramInventory owns a local, decoupled Pydantic implementation of the Stage F protocol. It does NOT import any classes from Brain Core. This ensures the AaramInventory application can boot and run entirely independently.
- `ContextCapabilityRequest`
- `ResolvedSemanticRequirement`
- `ContextCapabilityResult`

### 2. Context Engine (`engine.py`)
The `ContextEngine` acts as the capability dispatcher. It holds a registry of capability URNs mapped to provider callables. When a request arrives, the engine lazily resolves the provider into a `BaseCapabilityHandler` and invokes it, ensuring that database sessions and service dependencies remain securely within the FastAPI request scope.

### 3. Dependency Injection (`dependency_injection.py`)
The `ContextContainer` securely bridges the CEM with existing `InventoryContainer` services. It lazily injects services like `BalanceCalculatorService` or `InventoryLedgerService` into the specific capability handlers.

### 4. API & Authorization (`src/api/v1/context_router.py`)
The CEM exposes a single generic endpoint:
`POST /api/v1/context/resolve`

**Security Model:**
1. **Application Identity:** The caller must provide a valid JWT with `"AARAM_BRAIN_APP"` in its `applications` list.
2. **Physical RBAC:** Every capability URN maps strictly to a physical AaramInventory permission. Even if the Brain Core requests a capability, if the URN maps to `INVENTORY_PRODUCT_VIEW`, the underlying physical API security check enforces that requirement.

---

## Exposed Capabilities

The following capabilities are officially registered and supported by the AaramInventory CEM:

| Capability URN | Physical Permission | Target Inventory Service | Semantic Constraints Mapped |
|----------------|---------------------|--------------------------|-----------------------------|
| `urn:aarambooks:inventory:capability:balance` | `INVENTORY_PRODUCT_VIEW` | `BalanceCalculatorService.recalculate_balance` | `inventory.entity.sku`<br>`inventory.entity.warehouse` |
| `urn:aarambooks:inventory:capability:ledger` | `INVENTORY_ACTIVITY_VIEW` | `InventoryLedgerService.generate_ledger` | `inventory.entity.sku`<br>`inventory.entity.posting_date` |
| `urn:aarambooks:inventory:capability:jobwork_status` | `INVENTORY_JOBWORK_VIEW` | `JobWorkService.get_custody_ledger` | `inventory.entity.jobwork_vendor`<br>`inventory.entity.sku` |
| `urn:aarambooks:inventory:capability:exception_status` | `INVENTORY_EXCEPTION_VIEW` | `InventoryExceptionService.get_open_exceptions_for_sku` | `inventory.entity.sku`<br>`inventory.entity.exception_date` |

---

## Request & Response Flow

### Example Request from Brain Core
```json
{
  "capability_urn": "urn:aarambooks:inventory:capability:balance",
  "requirement": {
    "requirement_id": "req-8b3d88e0-1234-4abc",
    "original_requirement": {
      "semantic_intent": "How many pillows are in the main warehouse?"
    },
    "core_identities": [],
    "semantic_constraints": [
      {
        "identity": "inventory.entity.sku",
        "operator": "EQUALS",
        "bound_value": "123e4567-e89b-12d3-a456-426614174000"
      },
      {
        "identity": "inventory.entity.warehouse",
        "operator": "EQUALS",
        "bound_value": "987e6543-e21b-12d3-a456-426614174111"
      }
    ]
  }
}
```

### Handler Processing (Internal)
1. The `BalanceCapabilityHandler` extracts the `bound_value` for `inventory.entity.sku` and `inventory.entity.warehouse`.
2. It validates the UUIDs.
3. It calls the existing inventory service: 
   `await balance_calculator.recalculate_balance(sku_id, warehouse_id)`
4. It receives the physical `StockBalance` model.

### Example Response to Brain Core
```json
{
  "status": "SUCCESS",
  "data": {
    "balance": 150,
    "confidence_score": 98.5
  },
  "provenance_metadata": {
    "source_system": "AARAM_INVENTORY",
    "retrieval_timestamp": "2026-08-29T10:00:00Z",
    "physical_evidence_type": "StockBalance"
  },
  "error_message": null
}
```

The Brain Core (Intelligence Domain) is then responsible for consuming this opaque `data` block, structuring the final human-readable response, and verifying the `confidence_score` according to its internal cognitive planners.
