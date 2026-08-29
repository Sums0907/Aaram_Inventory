import pytest
from httpx import AsyncClient
from uuid_extensions import uuid7

@pytest.mark.asyncio
async def test_resolve_capability_unauthorized(async_client: AsyncClient):
    # The async_client fixture injects a user with specific permissions.
    # We test a capability that requires a permission they don't have, OR we just 
    # test that the mock user has it and verify the route resolves.
    # The mock user has 'INVENTORY_PRODUCT_VIEW' but let's see what happens.
    
    payload = {
        "capability_urn": "urn:aarambooks:inventory:capability:balance",
        "requirement": {
            "requirement_id": "req-123",
            "original_requirement": {
                "semantic_intent": "get balance"
            },
            "core_identities": [],
            "semantic_constraints": [
                {
                    "identity": "inventory.entity.sku",
                    "operator": "EQUALS",
                    "bound_value": str(uuid7())
                },
                {
                    "identity": "inventory.entity.warehouse",
                    "operator": "EQUALS",
                    "bound_value": str(uuid7())
                }
            ]
        }
    }
    
    # We override the dependency for just this test to ensure it fails authorization
    from src.app.main import app
    from src.foundation.authentication.dependencies import get_current_user, CurrentUser
    mock_unauth = CurrentUser(
        user_id="unauth-123",
        name="unauth",
        applications=["AARAM_BOOKS"],
        roles=[],
        permissions=[]
    )
    app.dependency_overrides[get_current_user] = lambda: mock_unauth
    
    response = await async_client.post("/api/v1/context/resolve", json=payload)
    app.dependency_overrides.pop(get_current_user, None)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "UNAUTHORIZED"
    assert "Missing required physical permission" in data["error_message"]

@pytest.mark.asyncio
async def test_resolve_capability_unregistered(async_client: AsyncClient):
    payload = {
        "capability_urn": "urn:aarambooks:unknown:capability",
        "requirement": {
            "requirement_id": "req-123",
            "original_requirement": {
                "semantic_intent": "unknown"
            },
            "core_identities": [],
            "semantic_constraints": []
        }
    }
    
    response = await async_client.post("/api/v1/context/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ERROR"
    assert "not registered" in data["error_message"]

@pytest.mark.asyncio
async def test_resolve_capability_provenance_metadata(async_client: AsyncClient):
    payload = {
        "capability_urn": "urn:aarambooks:inventory:capability:ledger",
        "requirement": {
            "requirement_id": "req-456",
            "original_requirement": {
                "semantic_intent": "get ledger"
            },
            "core_identities": [],
            "semantic_constraints": [
                {
                    "identity": "inventory.entity.sku",
                    "operator": "EQUALS",
                    "bound_value": str(uuid7())
                },
                {
                    "identity": "inventory.entity.posting_date",
                    "operator": "GREATER_THAN_EQUALS",
                    "bound_value": "2026-08-01T00:00:00Z"
                }
            ]
        }
    }
    
    response = await async_client.post("/api/v1/context/resolve", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("DEBUG DATA:", data)
    
    assert data["status"] in ["SUCCESS", "DATA_UNAVAILABLE"]
    
    # Verify exact Stage F field naming
    assert "provenance_metadata" in data
    assert data["provenance_metadata"] is not None
    assert "retrieval_timestamp" in data["provenance_metadata"]
    
    # Verify provenance does NOT exist
    assert "provenance" not in data
