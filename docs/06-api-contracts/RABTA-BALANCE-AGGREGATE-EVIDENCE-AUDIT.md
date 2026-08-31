# RABTA-BALANCE-AGGREGATE-EVIDENCE-AUDIT

## Executive Verdict
**Averaging confidence scores is architecturally flawed and unnecessary.** The Inventory business domain's `ConfidenceEngine` already natively supports calculating confidence at the global SKU level (when `warehouse_id=None`), just as `InventoryMovementRepository` natively supports calculating global balance. The CEM adapter can directly invoke these authoritative domain services to construct a fully populated aggregate evidence response without hallucinating or synthetically averaging any data.

## Current Balance Evidence Structure
Currently, both `R4BalanceCapability.fetch_evidence` and `BalanceCapabilityHandler` return a flat dictionary structure:
```json
{
    "sku_id": "UUID",
    "warehouse_id": "UUID",
    "total_quantity": 100.0,
    "on_hand_quantity": 100.0,
    "confidence_score": 95.0,
    "last_calculated_at": "ISO-8601"
}
```
This structure fundamentally assumes a single warehouse entity.

## Current Confidence/Provenance Semantics
Confidence is calculated by the `ConfidenceEngine.calculate_confidence(sku_id: UUID, warehouse_id: Optional[UUID] = None)` method. The engine checks for:
1. Open exceptions (Marketplace, Accounting, Physical discrepancies).
2. Negative inventory balances mathematically.
3. Manual adjustments.

## Global Balance Evidence
For global balance, the `InventoryMovementRepository` exposes `get_global_balance(sku_id)`. The `ConfidenceEngine` is already designed to accept `warehouse_id=None`, allowing it to evaluate exceptions and movements across the entire SKU. Therefore, authoritative global evidence is natively supported by the domain without needing to query individual warehouses.

## Warehouse Balance Evidence
For a specific warehouse, the domain provides `InventoryMovementRepository.get_balance(warehouse_id, sku_id)` and a materialized view in `InventoryBalanceRepository.get_balance()`.

## Whether Confidence Averaging is Justified
**Confidence averaging is NOT justified.** 
1. **Mathematical Flaw**: An exception in one warehouse (e.g., negative inventory) represents a systemic operational fault for the SKU. Averaging it with 10 "perfect" warehouses dilutes the fault, leading to artificially high confidence. 
2. **Architectural Redundancy**: The domain's `ConfidenceEngine` already possesses the explicit semantic capability to calculate global confidence by evaluating all open exceptions and movements for a SKU. The CEM should delegate to the engine, not reinvent confidence math.

## Correct Evidence Contract for Aggregate Balance
The response should omit `warehouse_id` (or set to `null`) and optionally embed a `warehouse_balances` breakdown for conversational richness.

```json
{
    "sku_id": "UUID",
    "warehouse_id": null,
    "total_quantity": 100.0,
    "on_hand_quantity": 100.0,
    "confidence_score": 90.0,
    "last_calculated_at": "ISO-8601",
    "warehouse_balances": {
        "UUID-1": 60.0,
        "UUID-2": 40.0
    }
}
```

## Exact Inventory CEM Files Requiring Modification
1. `src/domains/context/capabilities/r4_balance_capability.py`
2. `src/domains/context/handlers/balance_handler.py`
3. `src/domains/inventory/repositories/movement.py` (to add a helper `get_warehouse_balances` grouping function, if needed for the breakdown).

## Exact Implementation Behavior Required
1. In `r4_balance_capability.py` and `balance_handler.py`, make the semantic constraint `inventory.entity.warehouse` optional.
2. If `warehouse_id` is present:
   - Call `balance_repository.get_balance(warehouse_id, sku_id)`. 
   - Fallback to `movement_repository.get_balance()` and `confidence_engine.calculate_confidence(sku, warehouse_id)`.
3. If `warehouse_id` is omitted:
   - Call `movement_repository.get_global_balance(sku_id)`.
   - Call `confidence_engine.calculate_confidence(sku_id, None)`.
   - Fetch the warehouse breakdown from `movement_repository`.
   - Return the combined evidence with `warehouse_id: None`.

## RABTA Impact
None. RABTA Brain Core remains strictly uncoupled from these business mechanics. When AaramBrain parses "What is the balance of SKU=123", it maps strictly to `intent=RETRIEVE` and `sku=123`. The modified Inventory CEM will accept this and return the global stock evidence.

## Certification Impact
This modification solidifies the R-4 and R-7 boundary separation. It aligns the CEM contract strictly with the actual capabilities of the authoritative domain, ensuring that physical/operational constraints (like warehouse) are only enforced where mathematically required (e.g., Goods Receipt), while analytical read-only queries (Balance) are as flexible as the domain permits.

## Exact Next Implementation Step
Implement the logical branch in `R4BalanceCapability.fetch_evidence` and `BalanceCapabilityHandler.handle` to execute the global sum (`get_global_balance`) and global confidence (`calculate_confidence(sku_id, None)`) when the warehouse semantic entity is missing.
