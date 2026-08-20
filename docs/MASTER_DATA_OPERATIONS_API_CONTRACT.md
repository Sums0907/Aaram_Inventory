# Master Data Operations API Contract

This document defines the exact API contracts implemented in Phase 2 for the Master Data Operations UI.

---

## 1. Import API

**Endpoint:** `POST /api/v1/master-data/import`

### Request

- **Content-Type:** `multipart/form-data`
- **Fields:**
  - `file`: `UploadFile` (The `.xlsx` or `.csv` dataset)
  - `domain`: `string` (e.g., `"RAW_MATERIAL"`, `"SUPPLIER"`, `"BOM"`, `"UOM"`, `"OPERATIONAL_CATEGORY"`)
  - `is_dry_run`: `boolean` (True for dry run preview, False for final commit)

### Authentication
- **Required roles:** `SUPER_ADMIN`

### Response Schema

Returns a JSON object containing the `ImportResult` alongside the newly generated `batch_id`.

```json
{
  "batch_id": "BATCH-A1B2C3D4",
  "entity_type": "RAW_MATERIAL",
  "total_records": 100,
  "created_count": 10,
  "updated_count": 80,
  "ignored_count": 5,
  "failed_count": 5,
  "ambiguous_count": 0,
  "row_results": [
    {
      "row_index": 1,
      "action": "CREATED",
      "entity_id": "9f8c6b7a-...",
      "identifier": "RM-001",
      "errors": []
    },
    {
      "row_index": 2,
      "action": "FAILED",
      "entity_id": null,
      "identifier": "RM-002",
      "errors": ["GST % cannot be negative."]
    }
  ],
  "global_errors": []
}
```

### Behaviour

**Dry Run (`is_dry_run=true`):**
- Calculates all diffs and performs full schema validation.
- Generates `batch_id`.
- Transaction is **rolled back** (No database mutation).
- Audit log is created and rolled back alongside the data (unless explicitly separated).
- No commit occurs.

**Commit (`is_dry_run=false`):**
- **COMMIT BLOCKED:** If `failed_count > 0` OR `ambiguous_count > 0`, the transaction is rolled back completely and a 400 Bad Request / 500 Server Error is thrown preventing partial commits.
- If successful, the transaction is **committed**.
- Audit log is persisted securely.

---

## 2. Export API

**Endpoint:** `GET /api/v1/master-data/export`

### Request

- **Query Parameters:**
  - None required to trigger full export (Currently exports all domains. `domain` filtering may be added if required).

### Authentication
- **Required roles:** `ADMIN`, `SUPER_ADMIN`

### Response

- **Type:** Binary File Download
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Filename:** `master_data_export.xlsx`
- **Supported Domains (Exported as individual sheets):**
  - Raw Material Export (Raw Materials, Suppliers, BOMs)
  - Operational Master Export (UoM, Categories)

---

## 3. Activity History API

**Endpoint:** `GET /api/v1/master-data/activity-history`

### Request

- **Query Parameters:**
  - `domain` (optional string): Filter by `entity_type` (e.g., `RAW_MATERIAL`)
  - `status` (optional string): Filter by status (e.g., `COMMITTED`, `DRY_RUN`, `FAILED`)
  - `skip` (optional int, default 0)
  - `limit` (optional int, default 50)

### Authentication
- **Required roles:** `ADMIN`, `SUPER_ADMIN`

### Response

Returns an array of audit log objects derived from `ImportAuditLogModel`.

```json
[
  {
    "id": "e4d3c2b1-...",
    "batch_id": "BATCH-A1B2C3D4",
    "filename": "raw_materials_Q3.xlsx",
    "entity_type": "RAW_MATERIAL",
    "environment": "prod",
    "executed_by_user_id": "a1b2c3d4-...",
    "status": "COMMITTED",
    "rollback_status": "SUCCESS",
    "records_processed": 100,
    "success_count": 95,
    "failure_count": 0,
    "start_time": "2026-08-18T10:00:00Z",
    "end_time": "2026-08-18T10:00:05Z"
  }
]
```

---

## 4. Frontend Integration Rules

The Frontend application **must strictly adhere** to the following boundaries:

- **Never implement import logic:** The frontend does not parse, compare, or diff the file contents. All data logic belongs in the backend.
- **Never interpret business rules:** Do not write frontend validation for things like "UoM type cannot change" or "Phone number matching". Rely entirely on the backend `ImportRowResult.errors` array.
- **Only display service responses:** The frontend acts as a pure presentation layer, displaying the JSON output of the `/import` dry run and providing a UI mechanism to call it again with `is_dry_run=false`.

---

## 5. Error Handling

### HTTP Status Codes

- **401 Unauthorized:** Authentication failure (Missing or invalid JWT).
- **403 Forbidden:** Permission failure (User lacks `ADMIN` or `SUPER_ADMIN` roles).
- **400 Bad Request:**
  - Invalid file type (Only `.xlsx` / `.csv` allowed).
  - File size exceeds limit (10MB).
  - Validation failure (e.g., missing columns, empty file).
- **500 Internal Server Error:**
  - Import failure (e.g., Database constraint violation, unhandled exception).
  - Commit Blocked exception (Failed/Ambiguous > 0 on commit).
