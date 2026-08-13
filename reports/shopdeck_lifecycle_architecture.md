# ShopDeck Lifecycle Architecture
**Phase A: ShopDeck Order Lifecycle Foundation**

## 1. Existing Relevant Architecture
- **Order Model**: `SalesOrderModel` (`src/domains/operations/models/sales_order.py`) tracks `external_order_id`, `order_date`, and `status`.
- **ShopDeck Import Model**: Handled in `src/domains/data_ingestion/services/adapters/shopdeck_order.py`.
- **Inventory Services**: The authoritative Inventory Truth engine is fully certified and completely isolated from this phase. No inventory movements will be generated.

## 2. Proposed Lifecycle Model
We will safely extend the existing `SalesOrderModel` to act as the primary lifecycle tracker and introduce two new entities to track configuration and history.

### A. Extending `SalesOrderModel`
We will add lifecycle fields to `SalesOrderModel` without replacing the raw ShopDeck `status`. The model will hold both the raw status and the derived state:
- `status`: String (The raw `current_shopdeck_status`)
- `lifecycle_state`: String (`ACTIVE` or `TERMINAL`)
- `delivered_date`: Date (nullable)
- `return_watch_until`: Date (nullable)
- `return_policy_id`: UUID (nullable)
- `return_window_days_at_delivery`: Integer (nullable)
- `terminal_date`: Date (nullable)
- `last_observed_at`: DateTime (nullable)

### B. New Model: `OrderStateTransitionModel`
A durable, idempotent history of state changes.
- `id`: UUID (Primary Key)
- `order_id`: UUID (Foreign Key to `SalesOrderModel`)
- `external_order_id`: String
- `old_status`: String (nullable)
- `new_status`: String
- `observed_at`: DateTime
- `event_date`: Date (nullable)
- `source_reference`: String (nullable)

**Database Constraint:** We will enforce idempotency at the database layer (e.g., a `UniqueConstraint` on `external_order_id`, `new_status`, and `observed_at`/`event_date` if applicable) to guarantee 0 duplicate transitions upon repeated identical report uploads.

### C. New Model: `CustomerReturnPolicyModel`
An effective-dated policy configuration (never hardcoded).
- `id`: UUID
- `effective_from`: Date
- `return_window_days`: Integer
- `is_active`: Boolean

When an order reaches `DELIVERED`, it will lock in the current active policy's `return_window_days`, calculating and freezing its `return_watch_until` date. Future policy changes will **not** retroactively affect older orders.

### D. Lifecycle Engine (`LifecycleEngine`)
The engine translates ShopDeck Status to Lifecycle State. It is NOT a simple ACTIVE/TERMINAL toggle, but a derivation:
```text
ShopDeck Status → Lifecycle Rules → Lifecycle State
```

**Status Matrix Mapping:**

*ACTIVE*
- PRINT
- PACK
- IN-TRANSIT
- HANDOVER
- RTO_ACKNOWLEDGED
- RTO_INITIATED
- DELIVERED (remains ACTIVE until its applicable Customer Return Window expires)

*TERMINAL*
- RTO_DELIVERED
- RETURNED
- CANCELLED INITIATED

**Unknown Status Handling:**
Any status not recognized in the matrix will be treated strictly as an **Import Exception** (`UnknownShopDeckStatusException`). It will NOT become a normal business lifecycle state and will prevent any transition or processing for that record.

## 3. Files to be Changed/Created
- `src/domains/operations/models/sales_order.py` (extend model)
- `src/domains/operations/models/lifecycle.py` (add transition & policy models)
- `src/domains/operations/schemas/lifecycle.py` (schemas & enums)
- `src/domains/operations/services/lifecycle_engine.py` (business logic)
- `tests/operations/test_lifecycle_engine.py` (test suite)

## 4. Database Changes
- Add new lifecycle columns to `operations_sales_orders`.
- Create `operations_order_state_transitions` table with idempotency constraints.
- Create `operations_return_policies` table.

## 5. Tests to be Added
Comprehensive test suites covering full lifecycle sequences, not just individual statuses:

1. **Normal delivery**: PRINT → PACK → IN-TRANSIT → HANDOVER → DELIVERED → TERMINAL after return window.
2. **RTO sequence**: IN-TRANSIT → RTO_ACKNOWLEDGED → RTO_INITIATED → RTO_DELIVERED.
3. **Return after delivery**: DELIVERED → RETURNED.
4. **Late RTO**: 10 Aug: DELIVERED → 19 Aug: RTO_INITIATED → 20 Aug: RTO_DELIVERED.
5. **Policy change test**: Verify an order delivered on Aug 13 under a 7-day policy retains a `return_watch_until` of Aug 20, even if the master policy changes to 10 days on Oct 1.
6. **Idempotency**: Verify repeated same-state observations (e.g., DELIVERED → DELIVERED) produce 0 duplicate transitions and 0 state changes.
7. **Unknown status exception**: Verify that an unknown string raises an exception and does not mutate lifecycle state.

## 6. Architectural Rules Honored
- **NO INVENTORY MOVEMENTS:** Phase A establishes the state layer only.
- **ISOLATED LIFECYCLE:** The certified Inventory Truth Engine remains completely untouched.
