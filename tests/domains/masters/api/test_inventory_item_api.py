import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_inventory_item(async_client: AsyncClient):
    # Setup dependencies
    cat_res = await async_client.post("/api/v1/masters/categories", json={"category_code": "API-CAT", "category_name": "API Cat"})
    cat_id = cat_res.json()["data"]["id"]

    uom_res = await async_client.post("/api/v1/masters/units-of-measure", json={"unit_code": "API-UOM", "unit_name": "API UOM", "short_name": "apiuom"})
    uom_id = uom_res.json()["data"]["id"]

    # /inventory-items is the composite endpoint: it creates the Product and SKU
    # together from a single payload and returns the resulting SKU.
    payload = {
        "item_type": "RAW_MATERIAL",
        "category_id": cat_id,
        "new_product_name": "API Item",
        "item_code": "API-ITEM",
        "uom_id": uom_id,
        "attribute_values": {"Color": "Red"}
    }

    response = await async_client.post("/api/v1/masters/inventory-items", json=payload)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["item_code"] == "API-ITEM"
    assert data["attribute_values"]["Color"] == "Red"
