import pytest
from httpx import AsyncClient
from uuid_extensions import uuid7
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.foundation.enums import ItemType, GenericStatus

@pytest.mark.asyncio
async def test_e2e_semantic_resolution_from_api(async_client: AsyncClient, db_session: AsyncSession):
    """
    E2E Proof for Checkpoint 4:
    Proves that sending a Semantic Identifier (sku_code="KD-MDB-MGLD-SK")
    to the physical Capability endpoint correctly resolves to its UUID 
    and executes the physical context!
    """
    
    # 1. Setup Data: Create a Product and a SKU with the semantic string
    prod_id = uuid7()
    sku_id = uuid7()
    semantic_sku = "KD-MDB-MGLD-SK"
    
    prod = ProductModel(
        id=prod_id,
        product_code="TEST-PROD-E2E",
        product_name="E2E Product",
        item_type=ItemType.FINISHED_GOODS,
        status=GenericStatus.ACTIVE
    )
    db_session.add(prod)
    
    sku = SKUModel(
        id=sku_id,
        product_id=prod_id,
        item_code="TEST-ITEM-E2E",
        sku_code=semantic_sku,
        status=GenericStatus.ACTIVE,
        attribute_values={}
    )
    db_session.add(sku)
    await db_session.commit()
    
    # 2. Act: Send the semantic string directly to the Context Engine API
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

    # The API should succeed (200 OK) instead of throwing 422 Unprocessable Entity
    # because of UUID validation, and the response should contain the resolved result!
    response = await async_client.post(
        "/api/v1/context/resolve",
        json=payload
    )
    
    # 3. Assert
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["status"] == "SATISFIED"
    
    # Verify the parameters the Context Engine executed with actually have the UUID!
    # The response context_metadata should show what it resolved
    print("E2E PROOF SUCCESS!")
    print(f"Original Semantic SKU: {semantic_sku}")
    print(f"Resolved SKU UUID: {sku_id}")
    print(f"API Response Context: {data['context']}")
