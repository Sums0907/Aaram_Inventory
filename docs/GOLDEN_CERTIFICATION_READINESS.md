# Golden Certification Readiness: Inventory Truth Engine

## Application

*   **Startup Command:** `uvicorn src.app.main:app --reload --port 8080` (ensure virtual environment is activated: `source venv/bin/activate`).
*   **Required Environment Variables:**
    *   `DATABASE_URL`: Connection string for the database (e.g., `sqlite+aiosqlite:///./inventory.db` or a Postgres URI).
    *   `DATABASE_ENV`: Set to `test` to allow certification database setup/teardowns (avoids safety block).
    *   `SHOPDECK_SALES_WAREHOUSE_CODE`: The code of the warehouse to use for all webhook inventory movements (must match a valid `warehouse_code` in the DB).
*   **Database Configuration:** Runs asynchronously via SQLAlchemy and async drivers (aiosqlite or asyncpg). 
*   **Webhook Configuration:** Webhooks are stateless and fully encapsulated in the internal integration boundaries without external queueing mechanisms.

## Packer Integration Boundary

*   **Receiver Endpoint:** `POST /api/v1/internal/webhooks/packer/events`
*   **Authentication Mechanism:** Internal service network trust. Currently, no explicit token authentication is required for this route.
*   **Expected Headers:** standard `Content-Type: application/json`.
*   **Accepted Event Types:**
    *   `PACKED`
    *   `RTO_RECEIVED`
    *   `CUSTOMER_RETURN_RECEIVED`

## Event Processing

The lifecycle of an inbound integration event strictly follows this flow:

**Webhook received**  
&nbsp;&nbsp;&nbsp;&nbsp;↓  
**PackerEventModel creation** (Guarantees idempotency on `event_id`)  
&nbsp;&nbsp;&nbsp;&nbsp;↓  
**InventoryMovement creation** (Translates physical event to inventory action)  
&nbsp;&nbsp;&nbsp;&nbsp;↓  
**Ledger update** (Atomic persistence of movement affecting current available stock)

## Database Observation

The external certification harness can observe the following database tables to verify integration integrity:

### `packer_events`
*   **Purpose:** The immutable log of all successfully processed physical events from Aaram Packer. Provides idempotency.
*   **Important Columns:** `id`, `event_id`, `event_type`, `order_id`, `awb`, `payload`, `processed_at`.
*   **Certification Relevance:** Verify that a dispatched webhook successfully reached the engine and was durably recorded without duplication.

### `inventory_movements`
*   **Purpose:** The atomic ledger of every single stock change in the warehouse.
*   **Important Columns:** `id`, `sku_id`, `warehouse_id`, `movement_type`, `quantity`, `reference_number` (maps to Order ID / AWB), `created_at`.
*   **Certification Relevance:** Verify the system properly translated a physical event (like `PACKED`) into the correct movement (e.g., `SALES_FULFILLMENT`) with the correct sign convention (negative for pack, positive for return).

### `warehouses`
*   **Purpose:** Defines the physical locations where stock is held.
*   **Important Columns:** `id`, `warehouse_code`, `warehouse_name`.
*   **Certification Relevance:** The `warehouse_code` must map to `SHOPDECK_SALES_WAREHOUSE_CODE` to allow movements to occur during testing.

### `skus` (SKU / Product Master)
*   **Purpose:** The master definitions of all valid physical items recognized by the system.
*   **Important Columns:** `id`, `sku_code`, `product_id`.
*   **Certification Relevance:** A test webhook will be rejected if the payload contains SKU codes that do not exist in this table. Test SKUs must be seeded here prior to running event certifications.
