import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_inventory_item(async_client: AsyncClient):
    # Setup dependencies
    cat_res = await async_client.post("/api/v1/masters/categories", json={"category_code": "API-CAT", "category_name": "API Cat"})
    cat_id = cat_res.json()["data"]["id"]
    
    uom_res = await async_client.post("/api/v1/masters/units-of-measure", json={"unit_code": "API-UOM", "unit_name": "API UOM", "short_name": "apiuom"})
    uom_id = uom_res.json()["data"]["id"]
    
    attr_res = await async_client.post("/api/v1/masters/product-attributes", json={"attribute_code": "API-ATTR", "attribute_name": "API Attr"})
    attr_id = attr_res.json()["data"]["id"]
    
    payload = {
        "item_code": "API-ITEM",
        "item_name": "API Item",
        "category_id": cat_id,
        "unit_of_measure_id": uom_id,
        "gst_rate": 18.0,
        "product_attribute_ids": [attr_id]
    }
    
    response = await async_client.post("/api/v1/masters/inventory-items", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["item_code"] == "API-ITEM"
    assert len(data["product_attribute_ids"]) == 1
    assert data["product_attribute_ids"][0] == attr_id
