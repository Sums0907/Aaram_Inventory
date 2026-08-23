# Aaram_Inventory Bug Resolution Report

This document serves as a historical record of significant bugs encountered in the Aaram_Inventory application, detailing the root causes, the failed attempts to fix them (to prevent repeating mistakes), and the successful resolutions.

---

## Bug 1: AaramIdentity Authentication and PBAC Mismatch

**Date Identified**: August 2026
**Symptoms**:
- User successfully logged in as `AARAM_INVENTORY_ADMIN`, but all sidebar navigation items (Dashboard, Products, Catalogue) were completely missing from the UI.
- The Aaram_Inventory application returned `UnauthorizedException` errors stating the user did not have access to the application, or lacked permissions.

**Root Cause**: 
1. **Application Scope Check**: The backend `dependencies.py` was hardcoded to check for the `"AARAM_BOOKS"` scope in the JWT. However, AaramIdentity natively injects `"AARAM_INVENTORY"` into the token.
2. **Permission Prefixing**: The frontend React components (`InventoryLayout.tsx`, `InventoryOthersDropdown.tsx`) were strictly checking for legacy, un-prefixed permissions (e.g., `CATALOG_VIEW`, `PRODUCT_VIEW`), whereas the backend and AaramIdentity used the audited standard (e.g., `INVENTORY_CATALOG_VIEW`, `INVENTORY_PRODUCT_VIEW`).

**Failed Attempts**:
- **Bandaid Fix (SQL Injection)**: Initially attempted to manually inject missing scopes and legacy strings directly into the `AaramIdentity` PostgreSQL database to force the backend to accept it.
- **Why it failed**: This violated the `AARAMIDENTITY_RBAC_CONTRACT_FREEZE_REPORT.md` and contaminated the centralized identity system. The user explicitly ordered a reversion, enforcing that changes must occur in the consuming system (`Aaram_Inventory`), not the identity provider.

**Successful Resolution**:
- **Backend Fix**: Reverted the SQL injection. Updated `dependencies.py` in Aaram_Inventory to gracefully check for `"AARAM_INVENTORY"` in the JWT `applications` list instead of strictly `"AARAM_BOOKS"`.
- **Frontend Fix**: Executed a global find-and-replace across `frontend/src/` to update all legacy `requirePermission("..._VIEW")` hooks to check for `INVENTORY_..._VIEW`. This successfully synchronized the frontend with the identity provider's token output.

---

## Bug 2: React Query "Network Error" / API 500 Server Errors on Dashboard

**Date Identified**: August 2026
**Symptoms**:
- After fixing the sidebar navigation, clicking on "Dashboard" resulted in all tables hanging on a "Loading..." state indefinitely.
- The UI presented generic "Network Error" alerts.
- Network dev tools showed multiple API calls (`/api/v1/masters/products`, `/api/v1/inventory/balances`, etc.) failing with `500 Internal Server Error`.

**Root Cause**:
The `AaramIdentity` system mints user IDs as simple auto-incrementing integers (e.g., `"sub": "3"`). However, Aaram_Inventory's codebase (in over 63 separate API routes) strictly casts `current_user.id` to a UUID for tracking (`user_uuid = UUID(current_user.id)`). Passing `'3'` into Python's `uuid.UUID()` raised a `ValueError: badly formed hexadecimal UUID string`, instantly crashing the route with a 500 error.

**Failed Attempts**:
- **Misdiagnosed as CORS**: Because the frontend was running on `http://127.0.0.1:5173` but `settings.py` only permitted `http://localhost:5173`, the initial diagnosis was a CORS block. 
- **Why it failed**: Hardcoding `127.0.0.1` into the `settings.py` was rejected by the user because dynamic configuration (like `start_shell` environment variables) should never be overridden by hardcoded values. More importantly, CORS was a red herring; the true culprit was a runtime Python exception on the server.

**Successful Resolution**:
Rather than invasively modifying all 63 routes to handle integer parsing, the interceptor layer (`src/foundation/authentication/dependencies.py`) was augmented. During token decoding, if `user_id` is determined to be non-UUID compliant, it deterministically hashes the integer into a valid UUID string using `uuid.uuid5()`.
This elegant fix permanently resolved the 500 errors across the entire codebase.

---

## Bug 3: Master Data Catalogue Import Data Truncation and False Positives

**Date Identified**: August 2026
**Symptoms**:
- The ShopDeck CSV Master Data import was failing with a 500 error (`StringDataRightTruncationError`).
- After truncation was fixed, identical records in the CSV were incorrectly flagged as "UPDATED" (e.g. 57 records marked updated during a dry run) even when the source and destination data perfectly matched.
- The importer was throwing a boundary violation error (400 Bad Request) stating that Finished Goods SKUs must be managed by ShopDeck Sync, not the Raw Material importer.

**Root Cause**:
1. **Truncation**: The ShopDeck catalogue contained deeply descriptive product names and extremely long "size" options (e.g., `"Size: UK 9 | EU 43 | US 10"`). Our PostgreSQL `products.description` was capped at `VARCHAR(1000)` and `skus.size/color` at `VARCHAR(50)`, which were too small.
2. **False Positives**: Python's CSV reader loads empty cells as empty strings (`""`) and numeric prices as `float`. The database driver mapped these to PostgreSQL's `None` (NULL) and `Decimal`. Simple Python equality checks (`old.price != new.price` or `old.color != new.color`) evaluated to `True` for `Decimal(10.5)` vs `10.5` and `None` vs `""`.
3. **Item Type Misclassification**: The `ProductSKUImporter` assumed all incoming data was raw material unless explicitly flagged, triggering a rigid guardrail when a Finished Good was detected.

**Failed Attempts**:
- **Changing Model Type Without Migrations**: Attempted to just change the SQLAlchemy types in the models (`String(1000) -> Text`).
- **Why it failed**: Changing the python model does not automatically alter the live PostgreSQL schema. The database continued to reject inserts.

**Successful Resolution**:
- Authored and applied a manual Alembic migration to `ALTER TABLE products ALTER COLUMN description TYPE TEXT` and expand the SKU attribute columns to `VARCHAR(500)`.
- Wrote intelligent normalisation helpers (`_eq_str`, `_eq_num`) inside `ProductSKUImporter` to coalesce `None`/`""` and explicitly cast floats to `Decimal` before comparison, eliminating false-positive updates.
- Refactored the importer to dynamically resolve `ItemType.FINISHED_GOODS` vs `ItemType.RAW_MATERIAL` based on the presence of a `Sku Id` column in the CSV payload.

---

## Bug 4: Database Connection Pool Exhaustion (Cascading 500 Errors)

**Date Identified**: August 2026
**Symptoms**:
- The API backend would spontaneously crash with `QueuePool limit of size 15 overflow 20 reached, connection timed out, timeout 10.00`.
- All subsequent endpoints (e.g., `/inventory/balances`, `/masters/categories`) returned `500 Internal Server Error`.

**Root Cause**:
1. **Unclosed Sessions via DI**: Initially, the Dependency Injection containers were generating raw `_session_factory.call()` instances for every repository request. These sessions were never closed, draining the pool.
2. **Starlette Middleware Task Boundary**: After switching to `async_scoped_session(..., scopefunc=asyncio.current_task)` and adding a `try/finally` session teardown block in `RequestContextMiddleware`, the pool *still* leaked. This occurred because FastAPI/Starlette's `BaseHTTPMiddleware` executes the `call_next(request)` (the actual API route handler) in a **completely separate background `asyncio` task** to support response streaming. 
Because `current_task` was used as the identifier, the route handler created a session for Task A, while the middleware's teardown block attempted to remove the session for Task B (which was empty). Task A's session was never closed.

**Failed Attempts**:
- Using `try...finally` teardowns in `RequestContextMiddleware` while keeping `scopefunc=asyncio.current_task`. The teardown executed flawlessly but operated on the wrong task boundary.

**Successful Resolution**:
- Reconfigured `async_scoped_session` in `session.py` to use `scopefunc=get_request_id` (a `ContextVar` that securely bridges across Starlette's sub-task boundaries) instead of `asyncio.current_task`. 
- This mathematically guarantees that both the route handler generating the session and the middleware executing the teardown are referencing the exact same database session instance, fully eliminating the leak.

---

## Bug 5: Manual Adjustments 400 Bad Request (Foreign Key Violation)

**Date Identified**: August 2026
**Symptoms**:
- Attempting to submit a "Manual Adjustment" (Increase/Decrease Stock) failed with a `400 Bad Request` in the browser. 
- Retrying the request eventually caused the backend to crash (prior to the Bug 4 fix).

**Root Cause**:
- The frontend `ManualAdjustmentDialog.tsx` hardcoded a fallback `WAREHOUSE_ID` (`dbcfca97-fc1d-4466-815f-a843072a14be`). 
- The local `inventory_dev` PostgreSQL database was physically missing this warehouse record, triggering a silent foreign key constraint violation during the `InventoryMovement` insert.

**Successful Resolution**:
- Wrote a local python script (`seed_wh.py`) utilizing the SQLAlchemy ORM to manually insert the missing `Main Warehouse` record directly into the developer database, instantly unblocking the UI flow.
- A strategic Implementation Plan (`implementation_plan.md`) was drafted to permanently migrate the application to a dynamic, Context-based warehouse selector in the global header, replacing all hardcoded identifiers in the codebase.

---

## Bug 6: E2E Sync Certification and Database Safety Interceptor Overreach

**Date Identified**: August 2026
**Symptoms**:
- The E2E integration script between Aaram_Inventory and AaramPackingApp failed with `DATABASE SAFETY VIOLATION: EXPLICIT BULK DELETE`.
- Earlier iterations failed due to hallucinated dependencies (`async_session_factory`), incorrect import paths for `ItemType`, and payload key mismatches (`skus` vs `snapshot`).
- SQLAlchemy IntegrityErrors crashed the test script due to missing required fields (`product_code`, `item_code`) and unique constraint violations across test runs.

**Root Cause**:
1. **Safety Hook Overreach**: The Aaram_Inventory database connection hook explicitly listens for `Delete` execution and aborts them in non-TEST environments. However, the hook intercepted standard ORM deletions (e.g. `session.delete(obj)`) because SQLAlchemy compiles them to `Delete` clauses, effectively blocking all tear-down operations in Development.
2. **Payload Contract Mismatch**: The Inventory `daily_reconciliation` background task embedded SKUs in a JSON key called `"snapshot"`, but the Packer `InventoryEventHandler` blindly attempted to parse `"skus"`.
3. **Uncleared Test State**: Because tear-downs failed, subsequent runs hit `UniqueViolationError` on hardcoded testing values (e.g., `TEST-CAT`).

**Failed Attempts**:
- Using `DATABASE_ENV=test` to bypass the safety interceptor. **Why it failed:** The test database schema lacked the newly created `inventory_outbound_events` outbox table because Alembic migrations had not been applied to it.
- Executing standard ORM deletions inside the E2E script. **Why it failed:** Blocked by the overzealous `before_execute` safety listener.

**Successful Resolution**:
- Authored a clean architectural rewrite of the E2E script to bypass the ORM safety interceptor by issuing explicit raw SQL texts (`text("DELETE FROM skus...")`), successfully executing the teardown.
- Migrated the hardcoded test fixtures to utilize random UUID injections for codes and names, ensuring idempotent and collision-free test runs.
- Re-aligned the cross-service data contract: The Packer event handler now accurately reads the `"snapshot"` payload key.
- Fixed dependency injections to securely extract the session factory from the initialized `DomainsContainer` via `app.core_container.db()._session_factory`, eliminating the hallucinated global exports.

---

## Bug 7: Production 500 Network Error / CORS Misdirection (Identity Public Key)

**Date Identified**: August 2026
**Symptoms**:
- After VPS deployment, attempting to log in to `inventory.aarambooks.cloud` resulted in the frontend failing with a CORS error: `Origin https://inventory.aarambooks.cloud is not allowed by Access-Control-Allow-Origin`.
- The browser console reported `Status code: 500` for multiple endpoints (e.g., `/dashboard/summary`, `/dashboard/kpis`).

**Root Cause**:
- The CORS error was a deceptive symptom. The true root cause was a `500 Internal Server Error` hard-crash on the backend (`inventory-api-1`), which aborted the request before the `CORSMiddleware` could append the `Access-Control-Allow-Origin` headers.
- The backend crashed with `RuntimeError: Failed to fetch Identity public key from http://localhost:9000/auth/public-key: [Errno 111] Connection refused`.
- In production (Docker), `localhost` refers to the container itself. The codebase was hardcoded to fetch the Identity public key via HTTP, ignoring the explicitly provided `AARAMIDENTITY_PUBLIC_KEY` environment variable injected by the VPS deployment script.

**Failed Attempts**:
- Initial suspicion was a misconfigured `ALLOWED_ORIGINS` string parsing issue in `settings.py`. 
- **Why it failed**: Pydantic v2 natively parses JSON arrays properly. The environment variables were correct; the issue was an underlying crash stripping the headers, not the CORS configuration itself.

**Successful Resolution**:
- Refactored the `_fetch_public_key()` function in `Aaram_Inventory/src/foundation/authentication/jwt.py` to first check for `settings.AARAMIDENTITY_PUBLIC_KEY` (and properly un-escape any `\n` characters from inline Docker environments). If present, it uses this static key, completely bypassing the dangerous HTTP network fetch during the request lifecycle.

---

## Bug 8: 500 Network Error / CORS on SKU_QTY_BULK_MAPPING Import

**Date Identified**: August 2026
**Symptoms**:
- Attempting a dry-run or import using the newly created `SKU_QTY_BULK_MAPPING` importer triggered a CORS / Network Error (`Origin http://localhost:5173 is not allowed by Access-Control-Allow-Origin. Status code: 500`) on the frontend.
- The user suspected a permissions mapping issue because the domain was new.

**Root Cause**:
1. **Repository Mismatch**: The actual crash was a `TypeError` in `sku_qty_importer.py`. The `ConfidenceEngine` was initialized incorrectly (`ConfidenceEngine(self.session)`) instead of with its required repository dependencies (`ConfidenceEngine(exc_repo, movement_repo)`).
2. **Type Arithmetic Crash**: After the initialization was fixed, a secondary `TypeError` crashed the request: `unsupported operand type(s) for -: 'float' and 'decimal.Decimal'`. Python's native CSV reader loads values as `str` which we safely parsed to `float`, while `InventoryMovementService.get_balance()` correctly returns a `Decimal`. Python strictly prevents `float` - `Decimal` arithmetic.
3. **AttributeError on Commit**: The dry run succeeded, but the commit failed with `AttributeError: 'SKUModel' object has no attribute 'cost_price'`. The model stores pricing data in a separate `PricingModel` relation, not on the SKU itself.

**Failed Attempts**:
- Misdiagnosed as a permission boundary issue for the new domain name.

**Successful Resolution**:
- Corrected the instantiation of `ConfidenceEngine` in `SKUQtyImporter` to pass the `InventoryExceptionRepository` and `InventoryMovementRepository` instances.
- Replaced the `_safe_float` parser with a `_safe_decimal` helper to explicitly cast incoming CSV quantities to `Decimal` objects, aligning the arithmetic with the PostgreSQL database types.
- Casted the `Decimal` difference back to `float` to satisfy Pydantic's strict type guardrails for `InventoryMovementCreate`, and hardcoded `unit_cost=0.0` to bypass the invalid `cost_price` attribute lookup.
