import asyncio
from httpx import AsyncClient
from uuid_extensions import uuid7

async def run_proof():
    semantic_sku = "KD-MDB-MGLD-SK"
    payload = {
        "capability_urn": "urn:aarambooks:inventory:capability:balance",
        "requirement": {
            "requirement_id": "req-e2e-1",
            "original_requirement": {
                "semantic_intent": "Get inventory balance for SKU"
            },
            "core_identities": [],
            "semantic_constraints": [
                {
                    "identity": "inventory.entity.sku",
                    "operator": "EQUALS",
                    "bound_value": semantic_sku  # STRING, NOT UUID!
                },
                {
                    "identity": "inventory.entity.warehouse",
                    "operator": "EQUALS",
                    "bound_value": str(uuid7())  # dummy warehouse UUID
                }
            ]
        }
    }

    async with AsyncClient() as client:
        # Assuming the local server is running on port 8000
        # If it's not, we'll need to start it or use the ASGITransport like before.
        pass

if __name__ == "__main__":
    asyncio.run(run_proof())
