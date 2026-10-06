# Infra Gateway Webhook API Contract

This document describes the API contract and data payload for physical fulfillment/return events transmitted to the **AaramBooks Inventory Truth Engine**.

Aaram_Inventory has **no direct integration with AaramPackerApp**. Physical events originate in the Packer app but are relayed exclusively through the **Infra Gateway**, which is the only authenticated caller of this endpoint. There is also no SKU/catalog sync between Inventory and Packer — that outbound sync has been retired.

## Core Architectural Principle
> **The Infra Gateway is the trusted relay for physical warehouse events.** When a packer physically packs an order (or a return is received) and the Infra Gateway relays that terminal event here, AaramBooks trusts it to generate the corresponding inventory movement.

## Webhook Endpoint

**POST** `/api/v1/internal/webhooks/packer/events`

### Authentication

Requires a Bearer JWT from AaramIdentity (M2M service token) carrying the `INVENTORY_ADJUSTMENT_CREATE` permission, or the `AARAM_INVENTORY_ADMIN`/`AARAM_BOOKS_ADMIN` role. The Infra Gateway acquires this via AaramIdentity's `/auth/service-token` endpoint and sends it as `Authorization: Bearer <token>`.

## Payload Schema (`PackerEventPayload`)

The payload schema is defined in [`src/domains/inventory/schemas/packer_webhook.py`](../src/domains/inventory/schemas/packer_webhook.py).

```json
{
  "event_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_type": "PACKED",
  "occurred_at": "2026-08-17T10:30:00Z",
  "order_id": "SHOPDECK-ORD-999",
  "awb": "FORWARD-AWB-123",
  "items": [
    {
      "sku": "SKU-ABC",
      "quantity": 1
    }
  ]
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `event_id` | `UUID4` | Unique, immutable identifier for the physical event. Used by AaramBooks to guarantee idempotency. |
| `event_type` | `str` | The type of physical event: `PACKED`, `RTO_RECEIVED`, or `CUSTOMER_RETURN_RECEIVED`. |
| `occurred_at` | `datetime` | The exact UTC timestamp when the physical event occurred in the warehouse. |
| `order_id` | `str` | The external business identity of the order (e.g., ShopDeck Order ID). For a return event, this must match the `order_id` used in that order's original `PACKED` event. |
| `awb` | `str` | The logistics tracking number (AWB) associated with the shipment. |
| `items` | `List[PackerEventItem]` | The array of SKUs and quantities involved in the event. |

### Item Definition (`PackerEventItem`)

| Field | Type | Description |
|---|---|---|
| `sku` | `str` | The exact SKU code. |
| `quantity` | `int` | The physical quantity. Must be greater than 0 — sign/direction is derived server-side from `event_type`. |

### Movement Effect by `event_type`

| `event_type` | Movement Type | Quantity Effect |
|---|---|---|
| `PACKED` | `SALES_FULFILLMENT` | `-quantity` per SKU |
| `RTO_RECEIVED` | `RTO_RETURN` | `+quantity` per SKU |
| `CUSTOMER_RETURN_RECEIVED` | `CUSTOMER_RETURN` | `+quantity` per SKU |

A return event is rejected with `400` if no prior `PACKED` movement exists for that `order_id` (physical-cycle validation).

## Webhook Reliability & Delivery Rules

1. **Idempotency:** AaramBooks relies on the `event_id` to ensure that duplicate webhook deliveries do not result in duplicate inventory movements. If AaramBooks has already successfully processed `event_id`, subsequent requests with the same ID will return a successful 200 response without altering inventory.
2. **Immutability:** Once an event is successfully processed, it cannot be modified. Any subsequent adjustments or corrections must be handled via separate inventory adjustment workflows, not by re-sending a modified webhook.
