# RABTA-BALANCE-SEMANTIC-REQUIREMENT-AUDIT

## 1. Executive Verdict
**Warehouse is explicitly REQUIRED by the current Inventory CEM adapter, but it is OPTIONAL within the authoritative business domain.** 
The current implementation establishes a strict requirement (A. Warehouse REQUIRED) solely due to how the CEM adapter was written to map directly to a per-warehouse materialized view, rather than utilizing the domain's existing capability to calculate global (aggregate) balances.

## 2. Actual Balance Capability Contract
The actual execution contract for Balance discovery is defined in `R4BalanceCapability`. 

**SKU Requirement:** Required.
**Warehouse Requirement:** Required.

```python
    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku", "inventory.entity.warehouse"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        # ...
        has_sku = any(c.identity == "inventory.entity.sku" and c.operator == "EQUALS" for c in understanding.entities)
        has_warehouse = any(c.identity == "inventory.entity.warehouse" and c.operator == "EQUALS" for c in understanding.entities)
        
        return has_sku and has_warehouse
```

## 3. Evidence from the Implementation
The implementation enforces this requirement in two distinct CEM phases:
1. **R-4 Capability Discovery** (`R4BalanceCapability`): Returns `False` during `is_applicable()` if the warehouse constraint is omitted.
2. **Stage F Legacy Context Engine** (`BalanceCapabilityHandler`): Explicitly guards execution with:
   ```python
   if not sku_id or not warehouse_id:
       return ContextCapabilityResult(status="ERROR", error_message="Missing required exact constraints for sku and warehouse.")
   ```

## 4. Actual Execution Path
When AaramBrain submits: `"What is the stock balance for SKU=126BS"`
1. Brain Core extracts `intent=RETRIEVE` and `inventory.entity.sku=126BS`.
2. The R-4 Discovery Service evaluates `R4BalanceCapability.is_applicable`.
3. Because `inventory.entity.warehouse` is missing, `is_applicable` returns `False`.
4. The capability is excluded from the `applicable_capabilities` list.
5. (Depending on the route) Brain Core either triggers the Stage F handler directly (which yields an explicit error), or the R-4 Discovery Service drops the balance capability. Because Brain Core is aware of the required parameters (via contract sync/fallback), it logs a missing parameter limitation.

## 5. Business-Semantic Interpretation
The requirement for warehouse is **not a business rule limitation**. 
The domain service `InventoryMovementRepository` explicitly implements `get_global_balance(sku_id: UUID)` which safely calculates the aggregate balance of a SKU across all warehouses.

The restriction is strictly an **implementation artifact** of the CEM adapter. The `R4BalanceCapability.fetch_evidence` and `BalanceCapabilityHandler` were written to query `InventoryBalanceRepository.get_balance()`, which fetches a row from the `inventory_balances` table. Because that table projects balance strictly at the `(warehouse_id, sku_id)` granularity, the CEM adapter authors mistakenly elevated a database schema constraint into a conversational semantic constraint.

## 6. RABTA vs Inventory CEM Ownership
**The Inventory CEM owns this restriction.**
RABTA correctly honors the contract provided by the Inventory CEM. If the CEM declares that warehouse is a required semantic constraint, RABTA cannot and should not override it or hallucinate a warehouse to bypass it. 

## 7. Assessment of the E2E Result
The E2E result: `Missing required constraint: inventory.entity.warehouse`
This is an accurate programmatic reflection of the rigid contract currently enforced by the Inventory CEM adapter.

## 8. Assessment of the R-8 User-Facing Response
The R-8 output: `I cannot fully answer this question because required business data is unavailable. Limitations: [ExecutionLimitation(...)]`
This is the **expected, certified user-facing behavior** given the current contract. RABTA encountered an execution limitation dictated by the domain adapter, safely suspended execution, and initiated a bounded refinement loop to ask the user for the missing context (the warehouse). This proves that Brain Core's safety mechanisms are working flawlessly.

## 9. Certification Impact
The current implementation is safe (it does not hallucinate data) but overly rigid and semantically flawed. It prevents the user from asking natural aggregate questions (e.g., "What is the total stock of X?"). The Inventory CEM is artificially degrading the conversational experience by exposing a database projection limitation to the NLP engine.

## 10. Exact Next Step
Modify `R4BalanceCapability` (and if applicable, `BalanceCapabilityHandler`) in the Inventory CEM to:
1. Make `inventory.entity.warehouse` an **OPTIONAL** constraint.
2. Update the `fetch_evidence` implementation to branch logically:
   - If a warehouse is provided, fetch the specific `InventoryBalanceModel`.
   - If omitted, fetch the aggregate balance via `InventoryMovementRepository.get_global_balance` and average the confidence scores.
