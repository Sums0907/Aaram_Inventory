import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_create_integration(async_client: AsyncClient):
    payload = {
        "integration_code": "API-TEST",
        "integration_name": "API Test Integration",
        "integration_type": "TEST"
    }
    
    response = await async_client.post("/api/v1/data-ingestion/integrations", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["integration_code"] == "API-TEST"
    assert data["integration_name"] == "API Test Integration"
