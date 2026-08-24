import uvicorn
import asyncio
from src.app.main import app
from src.foundation.authentication.dependencies import get_current_user, CurrentIdentityContext

async def mock_get_current_user():
    return CurrentIdentityContext(
        user_id="a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
        name="Test User",
        applications=["AARAM_INVENTORY"],
        roles=["ADMIN"],
        permissions=["INVENTORY_MASTER_DATA_EXPORT"]
    )

app.dependency_overrides[get_current_user] = mock_get_current_user

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
