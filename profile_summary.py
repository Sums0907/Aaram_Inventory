import asyncio
import time
from httpx import AsyncClient, ASGITransport
from src.app.main import app
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from dependency_injector import providers
from src.foundation.database.session import Database

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def main():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id="00000000-0000-0000-0000-000000000001",
        username="admin",
        email="admin@aarambooks.com",
        role="SUPER_ADMIN",
        tenant_id="00000000-0000-0000-0000-000000000001"
    )
    app.core_container.db.override(
        providers.Singleton(Database, db_url=TEST_DATABASE_URL, debug=False, pool_size=1, max_overflow=0)
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.get("/api/v1/dashboard/summary")
        
        start = time.perf_counter()
        for _ in range(10):
            res = await client.get("/api/v1/dashboard/summary")
            assert res.status_code == 200
        end = time.perf_counter()
        
        print(f"Average Response Time: {(end - start) * 1000 / 10:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main())
