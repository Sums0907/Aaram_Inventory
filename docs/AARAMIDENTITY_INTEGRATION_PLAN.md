# AaramIdentity Integration Plan

This document outlines the architectural approach for integrating the shared **AaramIdentity** authentication service across the AaramBooks Inventory and AaramPacking System.

## 1. Frontend Integration

The frontend uses the `useAuth` hook strictly as an adapter/interface layer for AaramIdentity.

**`useAuth` responsibilities:**
- Expose the current user identity.
- Expose authentication status (`isAuthenticated`).
- Expose granular claims/permissions.
- Expose application access rights.

**Example Signature:**
```json
{
  "user_id": "a1b2c3d4-...",
  "name": "Jane Doe",
  "permissions": ["CAN_IMPORT_MASTER_DATA", "CAN_EXPORT_MASTER_DATA"],
  "applications": ["INVENTORY", "PACKING"],
  "isAuthenticated": true
}
```

Frontend components consume this information for UX visibility rules only. They **must not** interpret authentication logic, decode JWTs manually, or store independent user state.

## 2. Backend Token Validation

**Flow:**
1. **User Login** → Authenticates with AaramIdentity
2. **AaramIdentity** → Issues JWT
3. **Inventory API** → Receives JWT in headers
4. **Token Validation** → Backend verifies JWT signature using shared secrets/keys
5. **User Identity Context** → Extracted into `CurrentUser` dependency
6. **MasterDataApplicationService** → Consumes identity securely

**Strict Rules:**
- Inventory APIs must validate AaramIdentity-issued tokens.
- Do not create Inventory user tables or sessions.
- Do not duplicate the authentication system.

## 3. RBAC Design

The UI and Backend must prefer **permission-based checks** over hardcoded role strings (e.g., `if role == SUPER_ADMIN`).

**Example Permissions:**
- `CAN_IMPORT_MASTER_DATA`
- `CAN_EXPORT_MASTER_DATA`
- `CAN_VIEW_MASTER_DATA_HISTORY`

AaramIdentity provides these claims within the token. The Inventory backend maps incoming claims to business permissions if necessary, and enforces them natively at the application service boundary.

## 4. Role Mapping

AaramIdentity manages global roles (e.g., `OWNER`, `ADMIN`, `PACKER`).

**Application Usage Context:**
- **AaramBooks Inventory:** Only `OWNER` / `ADMIN` equivalent permissions have access. `PACKER` has no Inventory access.
- **Packing System:** `OWNER`, `ADMIN`, and `PACKER` have access based on their specific application rules.

These roles are never duplicated inside the Inventory schema.

## 5. Audit Identity Propagation

The identity of the user flows uninterrupted from AaramIdentity to the database audit logs.

**Flow:**
`AaramIdentity user_id` → `Inventory API Context` → `MasterDataApplicationService` → `ImportAuditLog.executed_by_user_id`

No local user identity duplication occurs in the Inventory system.
