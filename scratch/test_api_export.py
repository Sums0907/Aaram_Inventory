import asyncio
from httpx import AsyncClient
from src.app.main import app
from src.foundation.authentication.dependencies import get_current_user, CurrentIdentityContext
import traceback

async def mock_get_current_user():
    return CurrentIdentityContext(
        user_id="a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
        name="Test User",
        applications=["AARAM_INVENTORY"],
        roles=["ADMIN"],
        permissions=["INVENTORY_MASTER_DATA_EXPORT"]
    )

app.dependency_overrides[get_current_user] = mock_get_current_user

async def test_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            response = await client.get("/api/v1/master-data/export?domain=BOM")
            print("Status:", response.status_code)
        except Exception as e:
            print("Exception:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())
