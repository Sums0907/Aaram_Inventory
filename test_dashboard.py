import sys
import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from jose import jwt

sys.path.insert(0, '/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory')
from src.foundation.configuration import get_settings
settings = get_settings()

async def main():
    with open('/Users/sumatidhingra/Documents/AaramBooks/AaramIdentity/backend/private.pem', 'r') as f:
        private_key = f.read()

    to_encode = {
        "sub": "1",
        "roles": ["OWNER"],
        "applications": ["AARAM_BOOKS", "AARAM_PACKING"],
        "permissions": ["PRODUCT_VIEW"],
        "name": "System Owner",
        "aud": "AARAM_ECOSYSTEM",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }

    token = jwt.encode(to_encode, private_key, algorithm="RS256")
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8100/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")

asyncio.run(main())
