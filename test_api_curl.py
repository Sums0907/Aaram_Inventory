import asyncio
import httpx
from src.foundation.authentication.jwt import create_access_token

async def test():
    # generate a valid token
    token = create_access_token({"sub": "96f83859f3464b57b32f29272f6837f2"})
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        resp = await client.get("/api/v1/masters/categories", headers={"Authorization": f"Bearer {token}"})
        print("Status:", resp.status_code)
        import json
        print(json.dumps(resp.json(), indent=2))

asyncio.run(test())
