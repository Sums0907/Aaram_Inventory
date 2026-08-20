# AaramBooks Permission Integration Contract (FROZEN)

This contract defines the finalized permission dependency structure for AaramBooks Inventory. AaramIdentity serves as the authoritative source for these roles and permissions. AaramBooks Inventory is strictly a consumer of this contract.

## 1. Application Scope

All operations within AaramBooks Inventory require the `AARAM_BOOKS` application scope. Cross-application isolation guarantees that tokens scoped strictly to `AARAM_PACKING` cannot access AaramBooks APIs, regardless of the permissions held.

## 2. Final Permission Catalogue (DOMAIN_ACTION_MODEL)

AaramBooks Inventory consumes the following permissions from the JWT payload:

| Domain | Permissions |
|---|---|
| **Catalog** | `CATALOG_VIEW` |
| **Products** | `PRODUCT_VIEW`, `PRODUCT_CREATE`, `PRODUCT_UPDATE` |
| **Goods Receipts** | `INVENTORY_RECEIPT_CREATE`, `INVENTORY_RECEIPT_VIEW` |
| **Purchase Returns** | `INVENTORY_RETURN_CREATE`, `INVENTORY_RETURN_VIEW` |
| **Adjustments** | `INVENTORY_ADJUSTMENT_CREATE` |
| **Verification** | `INVENTORY_VERIFICATION_EXECUTE` |
| **Exceptions** | `INVENTORY_EXCEPTION_VIEW`, `INVENTORY_EXCEPTION_RESOLVE` |
| **Transformations** | `INVENTORY_TRANSFORMATION_CREATE` |
| **Job Worker Stock** | `INVENTORY_JOBWORK_VIEW`, `INVENTORY_JOBWORK_MANAGE` |
| **Activity History** | `INVENTORY_ACTIVITY_VIEW` |

## 3. Approved Role Mappings

| Role | Finalized Application Scope | Permission Access within AaramBooks |
|---|---|---|
| **OWNER** | `AARAM_BOOKS`, `AARAM_PACKING`, `*` | Complete unrestricted access. |
| **AARAM_BOOKS_ADMIN** | `AARAM_BOOKS` | All `AARAM_BOOKS` permissions. |
| **AARAM_BOOKS_INVENTORY_MANAGER** | `AARAM_BOOKS` | Operational inventory permissions including `INVENTORY_JOBWORK_MANAGE`, `INVENTORY_RECEIPT_VIEW`, and `INVENTORY_EXCEPTION_VIEW`. Restricted from High-Risk modifications like Adjustments and Transformations. |
| **AARAM_BOOKS_ACCOUNTANT** | `AARAM_BOOKS` | Strictly Accounting permissions plus `INVENTORY_ACTIVITY_VIEW`. |
| **AARAM_PACKING_OPERATOR** | `AARAM_PACKING`, `AARAM_BOOKS` | Cross-application read-only access strictly limited to `INVENTORY_JOBWORK_VIEW` within AaramBooks. |

*Note: The previously proposed `AARAM_BOOKS_INVENTORY_SUPERVISOR` role has been formally rejected and removed from the RBAC mapping model.*

## 4. Risk Classifications

- **Restricted to OWNER / AARAM_BOOKS_ADMIN (High Risk)**:
  - `INVENTORY_ADJUSTMENT_CREATE`
  - `INVENTORY_TRANSFORMATION_CREATE`
  - (These capabilities are strictly withheld from Inventory Managers due to audit sensitivity).

- **Allowed for Inventory Manager (Medium Risk)**:
  - `INVENTORY_JOBWORK_MANAGE`
  - `INVENTORY_RECEIPT_CREATE`
  - `INVENTORY_RETURN_CREATE`

## 5. Authorization Enforcement Flow

AaramBooks Inventory will enforce access strictly following this flow:

1. **JWT** extraction
2. **CurrentIdentityContext** generation
3. **Application scope validation** (`AARAM_BOOKS` required)
4. **Permission validation** (`require_permission` logic)
5. **Domain execution**

> **Contract Note:** AaramBooks Inventory consumes Identity-approved permissions. Inventory does not create or manage permissions.
