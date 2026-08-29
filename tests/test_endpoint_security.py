import pytest
from httpx import AsyncClient, ASGITransport
from src.app.main import app
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from uuid_extensions import uuid7

def override_auth(applications, permissions):
    mock_user = CurrentUser(
        user_id=str(uuid7()),
        name="test_user",
        applications=applications,
        roles=[],
        permissions=permissions
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user

@pytest.mark.asyncio
async def test_endpoint_security_valid_permission():
    """Test that a user WITH the right permission gets 200 (or validation error, not 401/403)."""
    override_auth(["AARAM_BOOKS"], ["INVENTORY_PRODUCT_CREATE"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/masters/products", 
            json={"name": "Test", "sku_code": "TEST", "category_id": "00000000-0000-0000-0000-000000000000", "uom_id": "00000000-0000-0000-0000-000000000000"}
        )
    # Could be 201 or 400 (validation), but NOT 401/403
    assert response.status_code not in (401, 403)
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_endpoint_security_missing_permission():
    """Test that a user WITHOUT the right permission gets 403."""
    override_auth(["AARAM_BOOKS"], ["INVENTORY_CATALOG_VIEW"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/masters/products", 
            json={"name": "Test", "sku_code": "TEST", "category_id": "00000000-0000-0000-0000-000000000000", "uom_id": "00000000-0000-0000-0000-000000000000"}
        )
    assert response.status_code == 403
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_endpoint_security_wrong_application():
    """Test that a user in the wrong application gets 403."""
    override_auth(["AARAM_PACKING"], ["INVENTORY_CATALOG_VIEW"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/masters/products", 
            json={"product_name": "Test", "product_code": "TEST"}
        )
    assert response.status_code == 403
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_endpoint_security_no_token():
    """Test that requests without a valid token get 401."""
    # Ensure no override
    app.dependency_overrides.clear()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/masters/products", json={"name": "Test"})
    assert response.status_code == 401
