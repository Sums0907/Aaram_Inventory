import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_unit(async_client: AsyncClient):
    payload = {
        "unit_code": "PKT",
        "unit_name": "Packet",
        "short_name": "pkt",
        "description": "Standard Packet"
    }
    
    response = await async_client.post("/api/v1/masters/units-of-measure", json=payload)
    assert response.status_code == 201
    
    data = response.json()["data"]
    assert data["unit_code"] == "PKT"
    assert data["status"] == "ACTIVE"
    assert "id" in data

@pytest.mark.asyncio
async def test_api_list_units(async_client: AsyncClient):
    # Ensure at least one unit exists
    payload = {
        "unit_code": "TON",
        "unit_name": "Tonne",
        "short_name": "t"
    }
    await async_client.post("/api/v1/masters/units-of-measure", json=payload)
    
    response = await async_client.get("/api/v1/masters/units-of-measure")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_api_update_unit(async_client: AsyncClient):
    # Create
    create_res = await async_client.post("/api/v1/masters/units-of-measure", json={
        "unit_code": "MM",
        "unit_name": "Millimeter",
        "short_name": "mm"
    })
    unit_id = create_res.json()["data"]["id"]
    
    # Update (omit unit_code)
    update_res = await async_client.put(f"/api/v1/masters/units-of-measure/{unit_id}", json={
        "unit_name": "Millimeter Updated",
        "short_name": "mm_upd"
    })
    
    assert update_res.status_code == 200
    assert update_res.json()["data"]["unit_name"] == "Millimeter Updated"
    assert update_res.json()["data"]["unit_code"] == "MM" # Remained unchanged
