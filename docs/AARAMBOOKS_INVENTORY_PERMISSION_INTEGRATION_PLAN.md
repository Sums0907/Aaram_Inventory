# AaramBooks Inventory Permission Integration Plan

This document outlines the strategy for mapping AaramBooks Inventory business workflows to AaramIdentity permissions. Following the certified Consumer Integration, AaramBooks will now enforce granular, domain-specific permissions for all Inventory routes.

## Phase 0: Permission Catalogue Freeze (FROZEN)

The permission catalogue has been finalized and frozen by AaramIdentity using the **DOMAIN_ACTION_MODEL**.

AaramBooks Inventory defines **REQUIRED capabilities**.
AaramIdentity owns:
- permission creation
- permission naming
- permission lifecycle
- role-permission mappings

> [!IMPORTANT]
> **Inventory consumes Identity-approved permissions. Inventory does not create or manage permissions.**

### Permission Dependency Table

| Inventory Capability | Required Identity Permission | Identity Role Mapping Owner |
|---|---|---|
| View Catalog | `CATALOG_VIEW` | AaramIdentity |
| View Products | `PRODUCT_VIEW` | AaramIdentity |
| Manage Products | `PRODUCT_CREATE`, `PRODUCT_UPDATE` | AaramIdentity |
| View Goods Receipts | `INVENTORY_RECEIPT_VIEW` | AaramIdentity |
| Create Goods Receipts | `INVENTORY_RECEIPT_CREATE` | AaramIdentity |
| View Purchase Returns | `INVENTORY_RETURN_VIEW` | AaramIdentity |
| Create Purchase Returns | `INVENTORY_RETURN_CREATE` | AaramIdentity |
| Create Adjustments | `INVENTORY_ADJUSTMENT_CREATE` | AaramIdentity |
| Execute Physical Verification | `INVENTORY_VERIFICATION_EXECUTE` | AaramIdentity |
| View Exceptions | `INVENTORY_EXCEPTION_VIEW` | AaramIdentity |
| Resolve Exceptions | `INVENTORY_EXCEPTION_RESOLVE` | AaramIdentity |
| Create Transformations | `INVENTORY_TRANSFORMATION_CREATE` | AaramIdentity |
| View Job Worker Stock | `INVENTORY_JOBWORK_VIEW` | AaramIdentity |
| Manage Job Worker Stock | `INVENTORY_JOBWORK_MANAGE` | AaramIdentity |
| View Activity History | `INVENTORY_ACTIVITY_VIEW` | AaramIdentity |

---

## Identity Role Mapping Summary

> [!NOTE]
> AaramIdentity owns role-permission mappings. Inventory only documents expected access requirements.

| Identity Role | Expected Inventory Capability |
|---|---|
| `OWNER` | Full access |
| `AARAM_BOOKS_ADMIN` | Full AARAM_BOOKS access |
| `AARAM_BOOKS_INVENTORY_MANAGER` | Operational inventory permissions + `INVENTORY_JOBWORK_MANAGE`, `INVENTORY_RECEIPT_VIEW`, and `INVENTORY_EXCEPTION_VIEW` |
| `AARAM_BOOKS_ACCOUNTANT` | Accounting permissions + `INVENTORY_ACTIVITY_VIEW` read-only |
| `AARAM_PACKING_OPERATOR` | Limited read-only view via `INVENTORY_JOBWORK_VIEW` cross-app scope |

---

## Permission Risk Classification

This classification helps AaramIdentity define safe role mappings.

**Low Risk:**
- View catalog
- View products
- Activity history

**Medium Risk (Allowed for Inventory Manager):**
- Goods receipts
- Purchase returns
- Transfers
- `INVENTORY_JOBWORK_MANAGE`

**High Risk (Restricted to OWNER/Admin):**
- `INVENTORY_ADJUSTMENT_CREATE`
- `INVENTORY_TRANSFORMATION_CREATE`

---

## Authorization Dependency Design

Before domain implementation, create centralized authorization dependency:

`require_permission(permission)`

**Flow:**
JWT
↓
CurrentIdentityContext
↓
Application scope validation
↓
Permission validation
↓
Domain execution

*(Avoid duplicating permission logic across services.)*

---

## Core Integration Principles
- **Application Scope**: All Inventory operations require the `AARAM_BOOKS` application claim.
- **Identity Authority**: AaramBooks Inventory purely consumes these permissions from the JWT `permissions[]` array. It does NOT define or create these permissions in its own database.
- **Backend Enforcement**: Route handlers must validate these required permissions via the `validate_permissions` service before allowing execution.
- **Frontend Enforcement**: Visibility of UI elements (menus, buttons, pages) must be governed by `useAuth().hasPermission()`.

---

## Domain Permission Mapping

### 1. Catalog
* **Current access control**: Authentication required (`get_current_user`), no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `CATALOG_VIEW`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/dashboard_router.py` (Catalog/Dashboard endpoints)
* **Required frontend visibility rule**: Hide "Catalog" from Inventory sidebar/navigation if missing.

### 2. Products
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `PRODUCT_VIEW`, `PRODUCT_CREATE`, `PRODUCT_UPDATE`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/masters/api/product.py` / `src/domains/inventory/api/item_workspace.py`
* **Required frontend visibility rule**: Hide "Products" tab. Disable "Edit" or "Create" buttons if Manage permission is missing.

### 3. Goods Receipts
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored as `created_by` in movements.
* **Required AaramIdentity permission**: `INVENTORY_RECEIPT_CREATE`, `INVENTORY_RECEIPT_VIEW`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/goods_receipt.py`
* **Required frontend visibility rule**: Hide "Goods Receipts" tab. Disable "Receive Goods" actions.

### 4. Purchase Returns
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored as `created_by`.
* **Required AaramIdentity permission**: `INVENTORY_RETURN_CREATE`, `INVENTORY_RETURN_VIEW`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/purchase_return.py`
* **Required frontend visibility rule**: Hide "Purchase Returns" tab. Disable "Initiate Return" actions.

### 5. Adjustments
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `INVENTORY_ADJUSTMENT_CREATE`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/movement_router.py`
* **Required frontend visibility rule**: Hide "Adjustments" from the Others dropdown. Disable "New Adjustment" button.

### 6. Verification
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `INVENTORY_VERIFICATION_EXECUTE`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/movement_router.py` (Verification endpoints)
* **Required frontend visibility rule**: Hide "Verification" tab. Disable physical verification workflows.

### 7. Exceptions
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `INVENTORY_EXCEPTION_VIEW`, `INVENTORY_EXCEPTION_RESOLVE`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/exception_router.py`
* **Required frontend visibility rule**: Hide "Exceptions" tab. Disable "Resolve" buttons.

### 8. Transformations
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `INVENTORY_TRANSFORMATION_CREATE`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/movement_router.py` (Transformation endpoints)
* **Required frontend visibility rule**: Hide "Transformations" tab. Disable "Start Transformation" workflows.

### 9. Job Worker Stock
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: User ID stored for audit logs.
* **Required AaramIdentity permission**: `INVENTORY_JOBWORK_VIEW`, `INVENTORY_JOBWORK_MANAGE`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/job_work.py`
* **Required frontend visibility rule**: Hide "Job Worker Stock" tab. Disable dispatch/receive job worker stock functions.

### 10. Activity
* **Current access control**: Authentication required, no permission guards.
* **Current user assumptions**: Read-only user context.
* **Required AaramIdentity permission**: `INVENTORY_ACTIVITY_VIEW`
* **Required application scope**: `AARAM_BOOKS`
* **Required backend guard location**: `src/domains/inventory/api/movement_router.py` (History endpoints)
* **Required frontend visibility rule**: Hide "Activity" tab. 

---

## Files Requiring Modification

### Backend
* `src/domains/inventory/api/dashboard_router.py`
* `src/domains/inventory/api/exception_router.py`
* `src/domains/inventory/api/goods_receipt.py`
* `src/domains/inventory/api/item_workspace.py`
* `src/domains/inventory/api/job_work.py`
* `src/domains/inventory/api/movement_router.py`
* `src/domains/inventory/api/purchase_return.py`
* `src/domains/inventory/api/router.py`
* `src/domains/inventory/services/inventory_application_service.py` (to inject `validate_permissions` similar to Master Data)

### Frontend
* `frontend/src/components/layout/InventoryLayout.tsx` (Sidebar Navigation)
* `frontend/src/components/layout/InventoryOthersDropdown.tsx` (Dropdown Navigation)
* Individual Domain Pages (`frontend/src/pages/inventory/*.tsx`) for button-level guards

---

## Implementation Phases

* **Phase 0: Permission catalogue freeze with AaramIdentity (COMPLETED)**
* **Phase 1: Centralized permission guard implementation**
* **Phase 2: Backend route/service authorization**
* **Phase 3: Frontend navigation guards**
* **Phase 4: Frontend action guards**
* **Phase 5: Security certification**
