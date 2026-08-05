import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_category(async_client: AsyncClient):
    payload = {
        "category_code": "PIL",
        "category_name": "Pillow Cover",
        "description": "Standard pillow covers",
        "display_order": 1
    }
    response = await async_client.post("/api/v1/masters/categories", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["category_code"] == "PIL"
    assert data["status"] == "active"
    assert "id" in data

@pytest.mark.asyncio
async def test_api_list_categories(async_client: AsyncClient):
    await async_client.post("/api/v1/masters/categories", json={
        "category_code": "CUSH",
        "category_name": "Cushion Cover"
    })
    
    response = await async_client.get("/api/v1/masters/categories")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_api_update_category(async_client: AsyncClient):
    create_res = await async_client.post("/api/v1/masters/categories", json={
        "category_code": "MAT",
        "category_name": "Mattress Protector"
    })
    cat_id = create_res.json()["data"]["id"]
    
    update_payload = {
        "category_name": "Mattress Protector Updated",
        "display_order": 5
    }
    
    update_res = await async_client.put(f"/api/v1/masters/categories/{cat_id}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["data"]["category_name"] == "Mattress Protector Updated"
    assert update_res.json()["data"]["category_code"] == "MAT" # Unchanged
    assert update_res.json()["data"]["display_order"] == 5
