# Master Data Operations - UI Implementation Plan

## 1. Overview
The "Master Data Operations" module provides a dedicated administrative interface to expose the existing, certified AaramBooks Master Data Import/Export engines. This UI will strictly wrap the existing backend domain services (Raw Material Sub-Engine and SKU Master Sub-Engine) without duplicating any business logic, ensuring all architectural boundaries and governance rules remain intact.

## 2. Page Structure & Navigation

**Route:** `/admin/master-data`

The module will be divided into three main tabs:
1. **Import Data:** For executing the multi-step import workflows.
2. **Export Data:** For triggering domain-specific exports.
3. **Master Data Activity History:** An audit log of all previous import and export events.

---

## 3. Import Workflow UI

The import process follows a strict wizard-style stepper to ensure explicit approval before database commits.

### Step 1: Upload & Domain Selection
- **Domain Selector:** Dropdown to select the target domain:
  - UoM
  - Operational Categories
  - Suppliers
  - Raw Materials
  - BOM
  - ShopDeck SKU Sync
- **File Upload:** Drag-and-drop or file selector (supports `.xlsx` and `.csv` depending on the domain).

### Step 2: Schema Validation & Dry Run
- **Pre-execution Validation:** Before executing a dry run, the system must validate:
  - File type (e.g., .xlsx, .csv)
  - File size (within limits)
  - Required sheets exist for the domain
  - Required columns exist in the sheets
- Invalid files are rejected immediately before any importer execution.
- If pre-validation passes, automatically calls the backend with `is_dry_run=True`.
- **Status Indicator:** Shows a spinner while processing.
- **Diff Preview Summary:** Displays high-level metrics grouped by entity:
  - <span style="color: green;">Created</span>
  - <span style="color: blue;">Updated</span>
  - <span style="color: gray;">Ignored</span>
  - <span style="color: red;">Failed</span>
  - <span style="color: orange;">Ambiguous</span>
- **Error/Ambiguity Table:** A detailed data table showing exactly which rows failed and why, directly rendering the `ImportRowResult.errors` list from the importer engine.

### Step 3: Admin Approval & Commit
- **Default behaviour:**
  - If `FAILED > 0` OR `AMBIGUOUS > 0`, then **COMMIT BLOCKED**.
  - The user must correct the file and retry.
  - No partial commit is allowed in the initial version.
- **"Confirm & Commit" Button:** Triggers the final backend call with `is_dry_run=False` (only enabled if Failed and Ambiguous are both 0).

### Step 4: Success & Audit Log
- Displays the final committed metrics.
- Shows the newly generated `Batch ID`.
- Button to download the full execution report or navigate to Import History.

---

## 4. Export UI

A simple interface to generate and download exact, round-trippable datasets.

- **Domain Selectors:**
  1. Raw Material Export (Outputs RM items, suppliers, BOMs)
  2. Operational Master Export (Outputs UoM, Categories)
- **Action:** "Generate Export" button triggers backend `MasterDataExporter.export_all()`.
- **Download:** Automatically downloads the resulting Excel payload to the browser.

---

## 5. Master Data Activity History UI

A data table listing historical synchronization, import, and export events.

**Columns:**
- **Batch ID:** Unique UUID for the execution.
- **File Name:** Name of the uploaded snapshot.
- **Domain:** Which entity/domain was imported or exported.
- **User:** The admin who executed it.
- **Timestamp:** Execution time.
- **Status:** `COMMITTED` / `DRY_RUN` / `FAILED` / `EXPORTED`.

---

## 6. Frontend Components Required

- `MasterDataTabs`: Navigation container for Import/Export/History.
- `ImportWizard`: State machine component managing the Upload -> Preview -> Commit flow.
- `EntityDiffCards`: Reusable metric cards displaying Created/Updated/Failed/Ignored counts.
- `ValidationDataTable`: Paginated table displaying `ImportRowResult` validation failures.
- `ExportPanel`: Simple form for triggering downloads.
- `HistoryTable`: Paginated data table for `ImportAuditLogModel` records.

---

## 7. Backend API Requirements

The backend will expose REST endpoints that act as clients to the application service layer.
**Important:** The UI API must not call CLI functions. The final architecture is:
```text
CLI ───────────────┐
                   ▼
       MasterDataApplicationService
                   ▼
      Importer/Exporter Engines
                   ▲
UI API ────────────┘
```
The UI API is just another client of the same `MasterDataApplicationService`.

### `POST /api/v1/master-data/import`
- **Payload:** `multipart/form-data` (file + `domain` + `is_dry_run` flag).
- **Controller Logic:** 
  - Resolves domain to the correct `BaseImporter` (e.g., `ProductSKUImporter`, `CategoryImporter`).
  - Calls `.import_data(df, is_dry_run=True/False)`.
  - Serializes `ImportResult` objects back to the frontend.

### `GET /api/v1/master-data/export`
- **Params:** `domain_group` (e.g., `RAW_MATERIAL`, `OPERATIONAL`).
- **Controller Logic:** 
  - Calls `MasterDataExporter.export_all()`.
  - Returns `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.

### `GET /api/v1/master-data/history`
- **Params:** Pagination & Filters.
- **Controller Logic:** Queries the `import_audit_logs` table (to be implemented or exposed if already existing).

---

## 8. Permission Model

**Strict Role-Based Access Control (RBAC):**

- **ADMIN Role:**
  - View activity history
  - Generate exports
- **SUPER_ADMIN Role:**
  - Upload imports
  - Execute dry runs
  - Commit imports
  - Generate exports

- **Enforcement:**
  - **Backend:** Fastapi Dependency `Depends(require_roles([...]))` checking the specific granular permission for each endpoint.
  - **Frontend:** The import actions will be disabled or hidden for non-SUPER_ADMIN users.

---

## 9. Integration Points & Architectural Rules

- **Zero Duplication:** The API layer acts **only** as a transport. It must instantiate `UOMImporter`, `CategoryImporter`, etc. and pass the DataFrame.
- **File Parsing:** The API endpoint must use `pandas` to parse the uploaded file into memory and pass the DataFrames to the existing engines exactly as `utils.py` or `manage_imports.py` does.
- **Audit Logging:** The backend API must capture the `executing_user` from the JWT token and pass it down to the engine or audit log table.
- **Transactions:** The UI commit phase relies entirely on the importer engine's atomic session flushes. The API endpoint does not manage transactions directly; it injects the request's scoped `AsyncSession` into the importer.
