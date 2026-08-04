import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_attribute(async_client: AsyncClient):
    payload = {
        "attribute_code": "SIZ",
        "attribute_name": "Size",
        "description": "Product size",
        "display_order": 1
    }
    response = await async_client.post("/api/v1/masters/product-attributes", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["attribute_code"] == "SIZ"
    assert data["status"] == "ACTIVE"
    assert "id" in data

@pytest.mark.asyncio
async def test_api_list_attributes(async_client: AsyncClient):
    await async_client.post("/api/v1/masters/product-attributes", json={
        "attribute_code": "FAB",
        "attribute_name": "Fabric"
    })
    
    response = await async_client.get("/api/v1/masters/product-attributes")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_api_update_attribute(async_client: AsyncClient):
    create_res = await async_client.post("/api/v1/masters/product-attributes", json={
        "attribute_code": "TC",
        "attribute_name": "Thread Count"
    })
    attr_id = create_res.json()["data"]["id"]
    
    update_payload = {
        "attribute_name": "Thread Count Updated",
        "display_order": 5
    }
    
    update_res = await async_client.put(f"/api/v1/masters/product-attributes/{attr_id}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["data"]["attribute_name"] == "Thread Count Updated"
    assert update_res.json()["data"]["attribute_code"] == "TC" # Unchanged
    assert update_res.json()["data"]["display_order"] == 5
