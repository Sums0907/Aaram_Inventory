import pytest
from httpx import AsyncClient

def get_payload(code, name):
    return {
        "warehouse_code": code,
        "warehouse_name": name,
        "address_line_1": "Road 1",
        "city": "Mumbai",
        "state": "MH",
        "pin_code": "400001"
    }

@pytest.mark.asyncio
async def test_api_create_warehouse(async_client: AsyncClient):
    payload = get_payload("BOM-01", "Bombay Hub")
    response = await async_client.post("/api/v1/masters/warehouses", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["warehouse_code"] == "BOM-01"
    assert data["status"] == "ACTIVE"
    assert "id" in data

@pytest.mark.asyncio
async def test_api_list_warehouses(async_client: AsyncClient):
    await async_client.post("/api/v1/masters/warehouses", json=get_payload("BOM-02", "Bombay Hub 2"))
    
    response = await async_client.get("/api/v1/masters/warehouses")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_api_update_warehouse(async_client: AsyncClient):
    create_res = await async_client.post("/api/v1/masters/warehouses", json=get_payload("BOM-03", "Bombay Hub 3"))
    wh_id = create_res.json()["data"]["id"]
    
    update_payload = get_payload("IGNORED", "Bombay Hub 3 Updated")
    del update_payload["warehouse_code"] # Omit code for update
    
    update_res = await async_client.put(f"/api/v1/masters/warehouses/{wh_id}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["data"]["warehouse_name"] == "Bombay Hub 3 Updated"
    assert update_res.json()["data"]["warehouse_code"] == "BOM-03" # Remained unchanged
