import asyncio
import os
os.environ["DATABASE_ENV"] = "test"
import sys
from uuid_extensions import uuid7

# Set up the paths and container
sys.path.append(os.getcwd())
from src.app.main import app
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.foundation.enums import ItemType, GenericStatus
from src.domains.context.contracts import SemanticConstraint, ResolvedSemanticRequirement, ContextCapabilityRequest

async def proof_e2e():
    print("STARTING E2E PROOF")
    
    # 1. Access DB from container
    db_singleton = app.core_container.db()
    
    prod_id = uuid7()
    sku_id = uuid7()
    semantic_sku = "KD-MDB-MGLD-SK"

    print("1. Injecting dummy data into the DB...")
    # Add dummy SKU directly to the DB to avoid API locks
    async with db_singleton._session_factory() as session:
        # Create a product first
        prod = ProductModel(
            id=prod_id,
            product_code="TEST-PROD-E2E-PROOF",
            product_name="E2E Product",
            item_type=ItemType.FINISHED_GOODS,
            status=GenericStatus.ACTIVE
        )
        session.add(prod)
        
        sku = SKUModel(
            id=sku_id,
            product_id=prod_id,
            item_code="TEST-ITEM-E2E-PROOF",
            sku_code=semantic_sku,
            status=GenericStatus.ACTIVE,
            attribute_values={}
        )
        session.add(sku)
        await session.commit()
    
    print(f"   -> Created SKU with code: {semantic_sku} and UUID: {sku_id}")
    print("2. Firing Context Request directly at the Context Engine...")
    
    engine = app.context_container.context_engine()
    
    req = ContextCapabilityRequest(
        capability_urn="urn:aarambooks:inventory:capability:balance",
        requirement=ResolvedSemanticRequirement(
            requirement_id="req-e2e-1",
            original_requirement={"semantic_intent": "get balance for sku"},
            core_identities=[],
            semantic_constraints=[
                SemanticConstraint(
                    identity="inventory.entity.sku",
                    operator="EQUALS",
                    bound_value=semantic_sku  # STRING, NOT UUID
                ),
                SemanticConstraint(
                    identity="inventory.entity.warehouse",
                    operator="EQUALS",
                    bound_value=str(uuid7())  # dummy UUID
                )
            ]
        )
    )
    
    print("   -> Request Constraints:")
    for sc in req.requirement.semantic_constraints:
        print(f"      - {sc.identity} = {sc.bound_value}")

    # ACT!
    result = await engine.resolve(req)
    
    print("\n3. RESULTS")
    print(f"Status: {result.status}")
    if result.context:
        print("Parameters returned by Handler (after Semantic Resolution):")
        for k, v in result.context.parameters.items():
            print(f"   - {k}: {v}")
            if k == "sku_id":
                assert v == str(sku_id), f"FAILED! Expected {sku_id}, got {v}"
                print("   [✓] SUCCESS! The UUID matches our Database ID!")
    else:
        print("No context returned.")
        print(result.errors)

if __name__ == "__main__":
    asyncio.run(proof_e2e())
