import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_sku(async_client: AsyncClient):
    # Setup dependencies
    cat_res = await async_client.post("/api/v1/masters/categories", json={"category_code": "SKU-CAT", "category_name": "SKU Cat"})
    cat_id = cat_res.json()["data"]["id"]
    
    uom_res = await async_client.post("/api/v1/masters/units-of-measure", json={"unit_code": "SKU-UOM", "unit_name": "SKU UOM"})
    uom_id = uom_res.json()["data"]["id"]
    
    item_res = await async_client.post("/api/v1/masters/inventory-items", json={
        "item_code": "SKU-ITEM",
        "item_name": "SKU Item",
        "category_id": cat_id,
        "unit_of_measure_id": uom_id,
        "gst_rate": 18.0
    })
    item_id = item_res.json()["data"]["id"]
    
    payload = {
        "sku_code": "SKU-TEST-1",
        "sku_name": "Test SKU 1",
        "inventory_item_id": item_id,
        "attribute_values": {"Color": "Red"},
        "gst_rate": 18.0
    }
    
    response = await async_client.post("/api/v1/masters/skus", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["sku_code"] == "SKU-TEST-1"
    assert data["attribute_values"]["Color"] == "Red"
