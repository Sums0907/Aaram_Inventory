# AARAMBOOKS DOMAIN AUTHORIZATION CERTIFICATION

This document certifies the comprehensive implementation of domain-level authorization in AaramBooks Inventory, using the external AaramIdentity system for centralized RBAC control.

---

## Domain Coverage Matrix

| Domain | Required Identity Permission | Backend Guard Location | Frontend Guard Location | API Endpoints Protected | Test Coverage |
|---|---|---|---|---|---|
| **Catalog** | `CATALOG_VIEW` | `src/api/v1/dashboard_router.py` | `InventoryLayout.tsx`, `InventoryOthersDropdown.tsx` | `GET /api/v1/dashboard/*` | Central mock token tests verified |
| **Products** | `PRODUCT_VIEW`, `PRODUCT_CREATE`, `PRODUCT_UPDATE` | `src/domains/inventory/api/product.py`, `item_workspace.py` | `ProductsPage.tsx`, `ProductWorkspaceDialog.tsx` | `GET/POST /api/v1/products`, `POST /api/v1/item-workspace/*` | Central mock token tests verified |
| **Goods Receipts** | `INVENTORY_RECEIPT_VIEW`, `INVENTORY_RECEIPT_CREATE` | `src/domains/inventory/api/goods_receipt.py` | `GoodsReceiptsPage.tsx` (Create Button) | `GET/POST /api/v1/goods-receipts` | Central mock token tests verified |
| **Purchase Returns** | `INVENTORY_RETURN_VIEW`, `INVENTORY_RETURN_CREATE` | `src/domains/inventory/api/purchase_return.py` | `PurchaseReturnsPage.tsx` (Create Button) | `GET/POST /api/v1/purchase-returns` | Central mock token tests verified |
| **Adjustments** | `INVENTORY_ADJUSTMENT_CREATE` | `src/domains/inventory/api/movement_router.py` | `AdjustmentsPage.tsx` (Action Button) | `POST /api/v1/movements/adjustments` | Central mock token tests verified |
| **Verification** | `INVENTORY_VERIFICATION_EXECUTE` | `src/domains/inventory/api/movement_router.py` | `PhysicalVerificationPage.tsx` | `POST /api/v1/movements/verification` | Central mock token tests verified |
| **Exceptions** | `INVENTORY_EXCEPTION_VIEW`, `INVENTORY_EXCEPTION_RESOLVE` | `src/domains/inventory/api/exception_router.py` | `ExceptionsPage.tsx` (Resolve Actions) | `GET/POST /api/v1/exceptions` | Central mock token tests verified |
| **Transformations** | `INVENTORY_TRANSFORMATION_CREATE` | `src/domains/inventory/api/movement_router.py` | `TransformationsPage.tsx` (Create Actions) | `POST /api/v1/movements/transformations` | Central mock token tests verified |
| **Job Worker Stock** | `INVENTORY_JOBWORK_VIEW`, `INVENTORY_JOBWORK_MANAGE` | `src/domains/inventory/api/job_work.py` | `JobWorkerStockPage.tsx` (Manage Actions) | `GET/POST /api/v1/job-work/*` | Central mock token tests verified |
| **Activity** | `INVENTORY_ACTIVITY_VIEW` | `src/domains/inventory/api/movement_router.py` | `ActivityPage.tsx` | `GET /api/v1/movements/activity` | Central mock token tests verified |

---

## Security Validation

The authentication and authorization pipeline `JWT → CurrentIdentityContext → Application scope validation → Permission validation → Domain execution` has been rigorously validated.

- **Valid AARAM_BOOKS identity succeeds**:
  Tested. When the `applications` claim includes `AARAM_BOOKS` and the `permissions` array includes the requisite permission (e.g., `INVENTORY_RECEIPT_CREATE`), access is granted and `user_id` is successfully propagated.
- **Missing permission returns 403**:
  Tested. Valid users attempting to access endpoints for which they lack specific granular permission (e.g., `INVENTORY_TRANSFORMATION_CREATE`) are consistently rejected with `HTTP 403 Forbidden` (`UnauthorizedException`/`ForbiddenException`).
- **AARAM_PACKING identity rejected**:
  Tested. Users strictly mapped to `AARAM_PACKING` without the `AARAM_BOOKS` application claim are instantly rejected via Application Scope Validation.
- **Invalid token rejected**:
  Tested. Tampered or improperly signed tokens are successfully rejected with `HTTP 401 Unauthorized`.
- **Expired token rejected**:
  Tested. Tokens past their `exp` timeframe natively fail signature validation and return `HTTP 401 Unauthorized`.

---

## Remaining Gaps

1. **Routes without authorization**:
   - Some operational APIs (e.g., Data Imports, Exports, specific webhook handlers) may currently lack explicitly bound permission guards pending further domain classification.
2. **UI actions without permission checks**:
   - Secondary actions within dialogs or configuration settings may need follow-up sweeps to ensure UI elements are completely hidden rather than solely relying on backend 403 rejection.
3. **Missing tests**:
   - While the centralized permission mechanism is verified via unit tests (`test_permissions.py`), dedicated integration tests asserting 403 responses across *every individual endpoint route* are not fully automated in the global `pytest` suite yet.


## Phase 6 Hardening Updates
- **Master Data (Catalog)**: Added `CATALOG_VIEW` to GET endpoints and `PRODUCT_CREATE`/`PRODUCT_UPDATE` to write endpoints across all master data APIs (`categories`, `products`, `units-of-measure`, etc.).
- **Job Worker Accounting**: Guarded with `INVENTORY_JOBWORK_VIEW` and `INVENTORY_JOBWORK_MANAGE`.
- **Connectors (ShopDeck)**: Guarded `/sync` with `PRODUCT_CREATE` and the read endpoints with `PRODUCT_VIEW`.
- **Frontend Sweep**: Wrapped the `Sync ShopDeck` button in the `Topbar.tsx` with `useAuth().hasPermission("PRODUCT_CREATE")`.
- **Automated Security Tests**: Added `tests/test_endpoint_security.py` verifying 200, 401, 403 enforcement for authenticated users and correct `AARAM_BOOKS` app scoping.
- **Identified Missing Permissions**: 
  - `MASTER_DATA_IMPORT`, `MASTER_DATA_EXPORT`, `MASTER_DATA_ACTIVITY_VIEW`, `ACCOUNTING_REPORTS` were NOT found in `AARAMBOOKS_PERMISSION_INTEGRATION_CONTRACT.md`.
  - Therefore, the `/data-ingestion` and `/accounting/export` routers remain unguarded pending an update from the Identity provider.
