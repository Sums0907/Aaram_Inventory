# Phase 0: Read-Only Architectural Audit

## Current Architecture
The Context Execution Module (CEM) currently operates via the `ContextEngine` (`src/domains/context/engine.py`), which acts as a blind dispatcher. It maps incoming `ContextCapabilityRequest` items (containing `SemanticConstraint` lists) to physical capability handlers (e.g., `BalanceCapabilityHandler`).

Currently, the handlers themselves iterate over the constraints and rigidly assume/cast values to UUID:
```python
if constraint.identity == "inventory.entity.sku":
    sku_id = uuid.UUID(str(constraint.bound_value))
```
This violates the generic principle by leaking physical DB schema assumptions (UUIDs) directly into the handler's constraint parsing logic, preventing semantic string lookup.

## Identified Interception Point
The semantic resolution must occur within `ContextEngine.resolve()` BEFORE the request is dispatched to the physical handler (`handler.handle(request)`). 
By running a pre-processing loop over the constraints through a `SemanticResolverRegistry`, we centralize the resolution logic and prevent handlers from needing to know how to resolve semantic concepts.

## Target Type Source
Currently, target types are hardcoded inside the handlers. To prevent the generic registry from assuming UUIDs, the physical handlers must become the source of truth for their target types.
We must extend `BaseCapabilityHandler` to declare its expected parameter contracts (e.g., `get_parameter_contracts() -> Dict[str, TargetType]`). `ContextEngine` will retrieve this contract and pass the expected `TargetType` down to the `SemanticResolver`, which will then yield a `TargetType` compatible system value.

## Authoritative Entity Source
- **SKU (`inventory.entity.sku`)**: `skus` table (`SKUModel` in `src/domains/masters/models/sku.py`). Potential lookup fields: `sku_code`, `item_code`, `shopdeck_sku_id`, `barcode`.
- **Warehouse (`inventory.entity.warehouse`)**: `warehouses` table (`WarehouseModel` in `src/domains/masters/models/warehouse.py`).
- **Job Worker (`inventory.entity.job_worker`)**: `masters_suppliers` table (`SupplierModel`).

## Risks
1. **DI Complexity**: Resolvers require database access. We must carefully wire the scoped `AsyncSession` into `ContextEngine` or the `SemanticResolverRegistry` via the `ContextContainer` without causing circular dependencies.
2. **Ambiguity**: If multiple SKUs match a string, resolution must deterministically fail with `AMBIGUOUS` rather than guessing.
3. **Contract Modification**: The `SemanticConstraint` model shouldn't just be mutated in-place loosely. We need a structured `EntityResolutionResult` to preserve the original `bound_value` for auditability while supplying the target system value to the handlers.

## Proposed Implementation Boundary
- `src/domains/context/engine.py` (Add pre-processing interceptor)
- `src/domains/context/handlers/base.py` (Add target parameter contract method)
- `src/domains/context/handlers/*.py` (Remove hardcoded UUID parsing; adopt resolved results)
- `src/domains/context/semantic_resolvers.py` (New: Registry, Protocols, SKU Resolver)
- `src/domains/context/contracts.py` (New DTOs for `EntityResolutionResult` and `TargetType`)
- `src/domains/context/dependency_injection.py` (Wiring DB to resolvers)

## Decision
**PASS** - The architecture clearly supports interception at the `ContextEngine` level, authoritative tables are identified, the target capability schemas can be exposed by the handlers, and Brain Core does not need any modifications.
