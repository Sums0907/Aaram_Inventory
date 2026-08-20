# AARAMBOOKS INVENTORY IDENTITY INTEGRATION PLAN

## Architectural Boundary Correction

**AaramIdentity owns:**
- Users
- Authentication
- Sessions
- Tokens
- Applications
- Roles
- Permissions
- RBAC mappings
- Access governance
- JWT issuance

**AaramBooks Inventory owns:**
- Inventory workflows
- Business rules
- Domain authorization enforcement
- Audit usage of identity information

*AaramBooks Inventory does NOT create or manage: users, roles, permissions, authentication, or RBAC definitions.*

---

## 1. Current Inventory Authentication State

### Backend Authentication
- **Existing Implementation:** Stateless JWT implementation located in `src/foundation/authentication/jwt.py`.
- **JWT Handling:** Uses symmetric `HS256` signing via the `jose` library.
- **Login Endpoints:** None exist.
- **User Models:** None exist in the database. In-memory `CurrentUser` model in `dependencies.py` has `id`, `username`, and a single `role`.
- **Session Management:** None exist (stateless).
- **Authorization:** Handled inside application services (e.g., `app_service.validate_permissions([current_user.role], ["SUPER_ADMIN"])`).
- **What needs replacement:** `HS256` validation needs to be replaced with AaramIdentity RS256 validation (fetching public key). Single `role` string needs to be replaced by `permissions[]` array.
- **What can be retained:** The stateless nature of the backend. `created_by` / `updated_by` UUID fields in database models which already accept arbitrary UUIDs (no FKs).

### Frontend Authentication
- **Login Flow:** None currently implemented.
- **Auth State Management:** Mocked via `src/hooks/use-auth.ts`, returning a hardcoded `mockUser` with `permissions[]` and `applications[]`.
- **Token Storage:** Hardcoded JWT in `src/api/client.ts`.
- **Interceptors:** Axios interceptor catches 403/401 errors and displays toast notifications, but no redirect to login exists.
- **Protected Routes:** `App.tsx` lacks `<ProtectedRoute>` wrappers. Role-based UI rendering is mocked in menus.

---

## 2. AaramIdentity Dependency Contract

Before implementation, Inventory must validate the Identity contract.

### JWT Contract
Verify:
- signing algorithm
- issuer
- audience
- expiry handling
- claims structure

Expected claims:
```json
{
 "sub": "user-id",
 "name": "user-name",
 "applications": [],
 "roles": [],
 "permissions": [],
 "exp": 123456
}
```
*Do not assume key distribution mechanism.* Inventory must follow the AaramIdentity-provided mechanism (e.g., JWKS endpoint, public key configuration, or other approved mechanism).

---

## 3. Backend Identity Integration Architecture

User
↓
AaramIdentity authentication
↓
JWT token
↓
Inventory API
↓
JWT validation
↓
CurrentIdentityContext
↓
Domain authorization

---

## 4. CurrentIdentityContext Design

**`CurrentIdentityContext`**

```python
from pydantic import BaseModel
from typing import List

class CurrentIdentityContext(BaseModel):
    user_id: str
    name: str
    applications: List[str]
    roles: List[str]
    permissions: List[str]
```
All Inventory domains should consume this object via FastAPI dependency injection. No domain should parse the JWT directly.

---

## 5. Authorization Consumption Model

### Identity-provided roles consumed by Inventory
AaramIdentity provides:
- `OWNER`
- `AARAM_BOOKS_ADMIN`
- `AARAM_BOOKS_INVENTORY_MANAGER`
- `AARAM_BOOKS_ACCOUNTANT`

Inventory consumes these claims from JWT. Inventory does not create, modify, or govern these roles.

### AaramIdentity-owned permissions consumed by Inventory
AaramIdentity owns permission creation and governance. Inventory consumes permissions for endpoint and workflow authorization.

Consumed permissions include:

**Inventory:**
- `INVENTORY_VIEW`
- `INVENTORY_RECEIVE`
- `INVENTORY_ADJUST`
- `INVENTORY_TRANSFER`
- `INVENTORY_VERIFY`
- `INVENTORY_ACTIVITY_VIEW`
- `INVENTORY_EDIT`

**Master Data:**
- `MASTER_DATA_IMPORT`
- `MASTER_DATA_EXPORT`
- `MASTER_DATA_ACTIVITY_VIEW`

**Accounting:**
- `ACCOUNTING_VIEW`
- `ACCOUNTING_ENTRIES`
- `ACCOUNTING_REPORTS`

---

## 6. Audit Identity Propagation

Migration of audit identity from local user identity to AaramIdentity user id (from JWT `sub` claim).

**Target Flow:**
JWT `sub`
↓
`CurrentIdentityContext.user_id`
↓
Audit fields (`created_by`, `updated_by`, `executed_by_user_id` on `ImportAuditLog`, etc.)

---

## 7. Frontend Identity Adapter

The `useAuth` hook in `frontend/src/hooks/use-auth.ts` will act as the AaramIdentity adapter.

Consume authentication/session mechanism provided by AaramIdentity according to Identity security contract.

**Frontend responsibilities:**
- Display current identity
- Consume `applications[]`
- Consume `roles[]`
- Consume `permissions[]`
- Control UX visibility

**Frontend must NOT:**
- validate JWT signatures
- create permissions
- implement authorization policy

---

## 8. Account Menu Permission Integration

Account menu visibility is controlled by Identity claims consumed through the adapter.

**Example: Master Data Operations visibility:**
Based on:
- `MASTER_DATA_IMPORT`
- `MASTER_DATA_EXPORT`
- `MASTER_DATA_ACTIVITY_VIEW`

*Backend remains the final authorization authority.*

---

## 9. Authorization Migration Audit

Before replacing existing authorization logic, audit all current Inventory authorization checks.
Search for `SUPER_ADMIN`, `ADMIN`, role comparisons, and permission checks.

Create a mapping from existing rules to AaramIdentity requirements. Do not blindly replace roles with permissions.

**Examples:**
- `SUPER_ADMIN` ↓ `OWNER` or `AARAM_BOOKS_ADMIN`
- Master Data import access ↓ `MASTER_DATA_IMPORT`
- Inventory adjustment access ↓ `INVENTORY_ADJUST`

---

## 10. Implementation Roadmap

- **Phase 0:** AaramIdentity Contract Validation
- **Phase 1:** Authorization Migration Audit
- **Phase 2:** Backend Identity adapter
- **Phase 3:** JWT validation
- **Phase 4:** CurrentIdentityContext
- **Phase 5:** Permission guards
- **Phase 6:** Frontend authentication adapter
- **Phase 7:** Remove legacy authentication

---
*AaramIdentity is the authority for authentication, applications, roles, permissions, and access governance. AaramBooks Inventory is a consuming application that validates Identity-issued tokens and enforces business authorization using Identity-provided claims.*
