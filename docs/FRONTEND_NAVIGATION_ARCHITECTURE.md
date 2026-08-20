# FRONTEND NAVIGATION ARCHITECTURE

**Status:** Approved Design — Source of Truth  
**Date:** 2026-08-19  
**Type:** Documentation only — No code changes in this document  

---

## 1. Navigation Design Principle

AaramBooks follows **ERP-style navigation**.

| Rule | Detail |
|---|---|
| Top navigation | Frequently used business workflows only |
| Administrative/system functions | Move under Account menu |
| Secondary inventory functions | Move under "Others" dropdown within Inventory |
| Existing routes | Must remain unchanged — only exposure and grouping change |
| Security authority | Backend remains security authority for all permissions |
| Frontend permission checks | UX-only visibility — not security enforcement |

---

## 2. Current State (Before Change)

### 2.1 Current Top Navigation (`Topbar.tsx`)

```
Dashboard   Imports   Matching   Inventory   Accounting   Exports   Settings
```

All items rendered as flat `Link` elements in `GLOBAL_NAV_ITEMS[]` array.  
The `User` icon (top right) is a static `<Button>` — no dropdown, no identity.

### 2.2 Current Inventory Sub-Navigation (`InventoryLayout.tsx`)

All 14 items rendered in a single flat horizontal scroll:

```
Dashboard · Catalog · Products · BOMs · UOMs · Suppliers · Goods Receipts ·
Purchase Returns · Activity · Verification · Adjustments · Exceptions ·
Transformations · Job Worker Stock · Confidence
```

### 2.3 Current Route Table (All Routes Preserved)

| Route | Component | Current Nav Location |
|---|---|---|
| `/dashboard` | `DashboardPage` | Top nav |
| `/imports` | `ImportsPage` | Top nav |
| `/matching` | `MatchingPage` | Top nav |
| `/exports` | `ExportsPage` | Top nav |
| `/settings` | `SettingsPage` | Top nav |
| `/inventory` | `InventoryPage` | Top nav → Inventory sub-nav |
| `/inventory/catalog` | `InventoryExplorerDashboard` | Inventory sub-nav |
| `/inventory/products` | `ProductsPage` | Inventory sub-nav |
| `/inventory/boms` | `BOMSetupPage` | Inventory sub-nav |
| `/inventory/units-of-measure` | `UnitsOfMeasurePage` | Inventory sub-nav |
| `/inventory/suppliers` | `SuppliersPage` | Inventory sub-nav |
| `/inventory/goods-receipts` | `GoodsReceiptsPage` | Inventory sub-nav |
| `/inventory/purchase-returns` | `PurchaseReturnsPage` | Inventory sub-nav |
| `/inventory/activity` | `ActivityPage` | Inventory sub-nav |
| `/inventory/verification` | `PhysicalVerificationPage` | Inventory sub-nav |
| `/inventory/adjustments` | `AdjustmentsPage` | Inventory sub-nav |
| `/inventory/exceptions` | `ExceptionsPage` | Inventory sub-nav |
| `/inventory/transformations` | `TransformationsPage` | Inventory sub-nav |
| `/inventory/job-worker-stock` | `JobWorkerStockPage` | Inventory sub-nav |
| `/inventory/confidence` | `ConfidencePage` | Inventory sub-nav |
| `/inventory/daily-update` | `DailyUpdatePage` | Hidden (commented out) |
| `/accounting` | `AccountingDashboardPage` | Top nav → Accounting sub-nav |
| `/accounting/job-worker/dashboard` | `JobWorkerAccountingDashboard` | Accounting sub-nav |
| `/accounting/job-worker/payables` | `JobWorkerPayablesWorkspace` | Accounting sub-nav |
| `/accounting/job-worker/rates` | `JobWorkRatesPage` | Accounting sub-nav |
| `/admin/master-data` | `MasterDataOperationsPage` | Hidden (no nav link) |

---

## 3. Target Navigation Architecture

### 3.1 Final Top-Level Navigation

```
[ AaramBooks logo ]   Dashboard   Inventory   Accounting   Account ▾
                                                           [ Sync ShopDeck ] [ Bell ] 
```

**Removed from top navigation (routes preserved):**
- ~~Imports~~ → moved to Account > Upcoming Modules
- ~~Matching~~ → moved to Account > Upcoming Modules
- ~~Exports~~ → moved to Account > Upcoming Modules
- ~~Settings~~ → moved to Account > System Settings

### 3.2 Account Menu (Dropdown)

The `User` icon in the top-right evolves into a full **Account** button/dropdown. It replaces the existing static `<Button>` icon.

```
Account ▾
├── [User display: name + role from AaramIdentity]
├── ─────────────────────────────
├── Account Settings          → /account/settings (future — placeholder for now)
├── System Settings           → /settings
├── ─────────────────────────────
├── Master Data Operations    → /admin/master-data
│     Permission: CAN_IMPORT_MASTER_DATA
│                 OR CAN_EXPORT_MASTER_DATA
│                 OR CAN_VIEW_MASTER_DATA_HISTORY
│     (Hidden entirely if user has none of these)
│
├── ─────────────────────────────
└── Upcoming Modules ▾
      ├── Matching             → /matching
      ├── Imports              → /imports
      └── Exports              → /exports
```

**Permission Behaviour for Master Data Operations:**
- If the user has **none** of the three Master Data permissions → the entire "Master Data Operations" item is hidden from the Account menu
- If the user has **at least one** → the item is visible and navigates to `/admin/master-data`
- Fine-grained tab visibility (Import / Export / History) is already handled inside `MasterDataOperationsPage` and `MasterDataTabs`

### 3.3 Inventory Primary Navigation (Redesigned)

The Inventory sub-nav bar (`InventoryLayout.tsx`) shows only **frequent operational workflows** by default. A new **Others** hover/click dropdown is appended at the end.

#### Primary Items (always visible):

```
Dashboard · Catalog · Products · Goods Receipts · Job Worker Stock · Activity · Exceptions · Others ▾
```

#### Others Dropdown (secondary, less-frequent):

```
Others ▾
├── Suppliers             → /inventory/suppliers
├── BOMs                  → /inventory/boms
├── UOMs                  → /inventory/units-of-measure
├── Purchase Returns      → /inventory/purchase-returns
├── Verification          → /inventory/verification
├── Adjustments           → /inventory/adjustments
└── Transformations       → /inventory/transformations
```

**Active state rule for Others:** If the current route belongs to any item inside the Others dropdown, the "Others" button itself should appear highlighted/active.

---

## 4. Final Navigation Tree

```
AaramBooks
│
├── Dashboard                          /dashboard
│
├── Inventory                          /inventory
│   ├── Dashboard                      /inventory
│   ├── Catalog                        /inventory/catalog
│   ├── Products                       /inventory/products
│   ├── Goods Receipts                 /inventory/goods-receipts
│   ├── Job Worker Stock               /inventory/job-worker-stock
│   ├── Activity                       /inventory/activity
│   ├── Exceptions                     /inventory/exceptions
│   └── Others ▾
│       ├── Suppliers                  /inventory/suppliers
│       ├── BOMs                       /inventory/boms
│       ├── UOMs                       /inventory/units-of-measure
│       ├── Purchase Returns           /inventory/purchase-returns
│       ├── Verification               /inventory/verification
│       ├── Adjustments                /inventory/adjustments
│       └── Transformations            /inventory/transformations
│
├── Accounting                         /accounting
│   ├── Dashboard                      /accounting
│   ├── JW Dashboard                   /accounting/job-worker/dashboard
│   ├── JW Payables                    /accounting/job-worker/payables
│   └── JW Rates                       /accounting/job-worker/rates
│
└── Account ▾                          (dropdown — no route)
    ├── [User identity display]
    ├── Account Settings               (placeholder — future)
    ├── System Settings                /settings
    ├── Master Data Operations         /admin/master-data
    │   (permission-gated)
    └── Upcoming Modules ▾
        ├── Matching                   /matching
        ├── Imports                    /imports
        └── Exports                    /exports
```

---

## 5. Route Preservation Guarantee

**All existing routes are preserved.** Only menu placement changes.

| Route | Preserved? | New Location |
|---|---|---|
| `/imports` | ✅ Yes | Account > Upcoming Modules |
| `/matching` | ✅ Yes | Account > Upcoming Modules |
| `/exports` | ✅ Yes | Account > Upcoming Modules |
| `/settings` | ✅ Yes | Account > System Settings |
| `/admin/master-data` | ✅ Yes | Account > Master Data Operations |
| `/inventory/suppliers` | ✅ Yes | Inventory > Others |
| `/inventory/boms` | ✅ Yes | Inventory > Others |
| `/inventory/units-of-measure` | ✅ Yes | Inventory > Others |
| `/inventory/purchase-returns` | ✅ Yes | Inventory > Others |
| `/inventory/verification` | ✅ Yes | Inventory > Others |
| `/inventory/transformations` | ✅ Yes | Inventory > Others |
| `/inventory/confidence` | ✅ Yes | Hidden (not in either menu — route works via direct URL) |
| `/inventory/daily-update` | ✅ Yes | Hidden (was already commented out in InventoryLayout) |

---

## 6. AaramIdentity Alignment

### 6.1 Account Menu Identity Display

The Account dropdown must display the authenticated user's information sourced from `useAuth()`:
- Display name
- Role label (OWNER / ADMIN / OPERATOR)

### 6.2 Permission-Gated Items

| Menu Item | Required Permission(s) | Behaviour if missing |
|---|---|---|
| Master Data Operations | Any of: `CAN_IMPORT_MASTER_DATA`, `CAN_EXPORT_MASTER_DATA`, `CAN_VIEW_MASTER_DATA_HISTORY` | Hidden from Account menu |
| Import tab (within Master Data) | `CAN_IMPORT_MASTER_DATA` | Tab hidden (existing behaviour) |
| Export tab (within Master Data) | `CAN_EXPORT_MASTER_DATA` | Tab hidden (existing behaviour) |
| Activity History tab | `CAN_VIEW_MASTER_DATA_HISTORY` | Tab hidden (existing behaviour) |

> **Constraint:** Frontend permission checks are UX only. Backend enforces all security boundaries.

### 6.3 Do Not Create

- Local user authentication in AaramBooks
- Duplicate user tables
- Duplicate permission systems

---

## 7. Component Change Plan (Implementation Reference)

This section describes which files change and what changes — for implementation phases only.

### 7.1 Files to Modify

| File | Change Summary |
|---|---|
| `frontend/src/components/layout/Topbar.tsx` | Replace `GLOBAL_NAV_ITEMS[]` with 3 items (Dashboard, Inventory, Accounting). Replace static User icon with Account dropdown component. |
| `frontend/src/components/layout/InventoryLayout.tsx` | Split `INVENTORY_NAV_ITEMS[]` into PRIMARY (8 items) and OTHERS (6 items). Add `Others` dropdown component at end of nav bar. |

### 7.2 Files to Create

| File | Purpose |
|---|---|
| `frontend/src/components/layout/AccountMenu.tsx` | New: Account dropdown button. Shows user identity, Account Settings, System Settings, Master Data Operations (permission-gated), Upcoming Modules. |
| `frontend/src/components/layout/InventoryOthersDropdown.tsx` | New: "Others" hover/click dropdown for secondary Inventory modules. Handles active-state detection. |

### 7.3 Files with No Change

| File | Reason |
|---|---|
| `frontend/src/App.tsx` | Routes are untouched. No route additions or deletions. |
| `frontend/src/pages/**` | All page components untouched. |
| `frontend/src/components/layout/AccountingLayout.tsx` | Accounting sub-nav is unchanged. |
| All backend files | Navigation is frontend-only change. |

---

## 8. Implementation Phases

| Phase | Task |
|---|---|
| **N-FE1** | Modify `Topbar.tsx` — remove Imports, Matching, Exports, Settings from top nav |
| **N-FE2** | Create `AccountMenu.tsx` — dropdown with Settings, Master Data, Upcoming Modules |
| **N-FE3** | Integrate `AccountMenu.tsx` into `Topbar.tsx` replacing static User icon |
| **N-FE4** | Modify `InventoryLayout.tsx` — split into primary + Others groups |
| **N-FE5** | Create `InventoryOthersDropdown.tsx` — hover dropdown with active state detection |
| **N-FE6** | Integrate `InventoryOthersDropdown.tsx` into `InventoryLayout.tsx` |
| **N-FE7** | Route preservation test — verify all 25 routes still load via direct URL |
| **N-FE8** | Permission visibility test — verify Master Data Operations gating |

---

## 9. Implementation Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Broken route links if nav items are accidentally removed instead of relocated | HIGH | `App.tsx` route definitions must not be touched. Only `Topbar.tsx` and `InventoryLayout.tsx` link arrays change. |
| Account dropdown z-index conflicts with Inventory sub-nav | MEDIUM | Account dropdown in Topbar has `z-50`. Inventory sub-nav has `z-10`. Ensure dropdown renders in Topbar layer. |
| "Others" active state not detected | MEDIUM | `InventoryOthersDropdown` must check if `location.pathname` matches any route in the Others group. |
| `useAuth()` mock permissions show all users as having Master Data access | LOW (dev only) | Current mock grants all 3 permissions. This is intentional for dev. Will resolve when AaramIdentity integration is live. |
| Mobile/small screen layout of Account dropdown | LOW | Topbar already has `hidden md:flex` on nav. Account button remains visible on all screen sizes. Dropdown must be tested on small screens. |
| `Confidence` page becomes unreachable via navigation | LOW | Route still works via direct URL. Acceptable — page is not in final nav tree by design. Document as intentional. |
