import pytest
import uuid
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from src.domains.context.dtos.integration_dtos import (
    AbstractEvidenceRequest, ConversationalUnderstanding, ClassifiedRequirement, ConversationalComponent,
    CandidateEntity
)
from src.domains.context.capabilities.r7_protocol import R7CapabilityRegistry
from src.domains.context.services.r7_execution_service import R7ExecutionService
from src.domains.context.semantic_resolvers import SemanticResolverRegistry
from src.domains.context.capabilities.r7_action_capabilities import (
    R7GoodsReceiptCapability, R7PurchaseReturnCapability, R7TransformationCapability,
    R7JobWorkIssueCapability, R7JobWorkReturnCapability, R7ExceptionResolutionCapability,
    R7StockAdjustmentCapability
)

# Dummy services for testing
class MockService:
    pass

@pytest.fixture
def r7_registry():
    registry = R7CapabilityRegistry()
    registry.register(R7GoodsReceiptCapability(MockService()))
    registry.register(R7PurchaseReturnCapability(MockService()))
    registry.register(R7TransformationCapability(MockService()))
    registry.register(R7JobWorkIssueCapability(MockService()))
    registry.register(R7JobWorkReturnCapability(MockService()))
    registry.register(R7ExceptionResolutionCapability(MockService()))
    registry.register(R7StockAdjustmentCapability(MockService()))
    return registry

@pytest.fixture
def semantic_registry():
    class MockSemanticRegistry(SemanticResolverRegistry):
        def __init__(self):
            pass
        def get_resolver(self, identity: str):
            class MockResolver:
                async def resolve(self, val, target):
                    from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
                    return EntityResolutionResult(
                        status=ResolutionStatus.RESOLVED,
                        semantic_identity=identity,
                        original_value=val,
                        resolved_value=val,
                        resolved_type="UUID",
                        target_type=target,
                        resolver_provenance="Mock"
                    )
            return MockResolver()
    return MockSemanticRegistry()

@pytest.fixture
def r7_service(r7_registry, semantic_registry):
    return R7ExecutionService(semantic_registry, r7_registry)

def test_r7_capability_exhaustion(r7_registry):
    """
    Programmatic exhaustion test for R-7 capability coverage.
    Ensures that every authoritative business intent identified in the R-7 Census
    has a registered execution capability.
    """
    expected_intents = {
        "inventory.action.receive",
        "inventory.action.return",
        "inventory.action.transform",
        "inventory.action.issue_jobwork",
        "inventory.action.return_jobwork",
        "inventory.action.resolve_exception",
        "inventory.action.adjust_stock"
    }

    covered_intents = set()
    for cap in r7_registry.get_all_capabilities():
        assert cap.supported_intent == "ACTION"
        
        # Test each expected intent to see if it is applicable
        for intent in expected_intents:
            understanding = ConversationalUnderstanding(
                intent="ACTION",
                entities=[
                    ConversationalComponent(identity=intent, operator="EQUALS", value="true", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.supplier", operator="EQUALS", value="uuid", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", value="uuid", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", value="uuid", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.job_worker", operator="EQUALS", value="uuid", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.exception", operator="EQUALS", value="uuid", original_expression="")
                ]
            )
            if cap.is_applicable(understanding):
                covered_intents.add(intent)

    missing_intents = expected_intents - covered_intents
    assert not missing_intents, f"Missing R-7 capabilities for intents: {missing_intents}"

@pytest.mark.asyncio
async def test_r7_execution_delegates_to_action(r7_service):
    """
    Proof that R-7 handles ACTION and maps correctly.
    """
    request = AbstractEvidenceRequest(
        classified_requirement=ClassifiedRequirement(
            understanding=ConversationalUnderstanding(
                intent="ACTION",
                entities=[
                    ConversationalComponent(identity="inventory.action.receive", operator="EQUALS", value="true", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.supplier", operator="EQUALS", value=str(uuid.uuid4()), original_expression=""),
                    ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", value=str(uuid.uuid4()), original_expression=""),
                    ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", value=str(uuid.uuid4()), original_expression="")
                ]
            )
        )
    )

    response = await r7_service.execute(request, {"application_id": "test"})
    assert response.status.name == "EXECUTION_LIMITATION"
    assert len(response.execution_limitations) == 1
    assert response.execution_limitations[0].missing_parameter == "capability_execution"

@pytest.mark.asyncio
async def test_r7_ambiguity_returns_limitation(r7_registry):
    """
    Proof that R-7 does not choose between ambiguous actions.
    """
    class AmbiguousSemanticRegistry(SemanticResolverRegistry):
        def __init__(self):
            pass
        def get_resolver(self, identity: str):
            class MockResolver:
                async def resolve(self, val, target):
                    from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
                    return EntityResolutionResult(
                        status=ResolutionStatus.AMBIGUOUS,
                        semantic_identity=identity,
                        original_value=val,
                        candidates=["uuid1", "uuid2"],
                        target_type=target,
                        resolver_provenance="Mock"
                    )
            return MockResolver()

    service = R7ExecutionService(AmbiguousSemanticRegistry(), r7_registry)
    
    request = AbstractEvidenceRequest(
        classified_requirement=ClassifiedRequirement(
            understanding=ConversationalUnderstanding(
                intent="ACTION",
                entities=[
                    ConversationalComponent(identity="inventory.action.receive", operator="EQUALS", value="true", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.supplier", operator="EQUALS", value=str(uuid.uuid4()), original_expression=""),
                    ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", value=str(uuid.uuid4()), original_expression=""),
                    ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", value=str(uuid.uuid4()), original_expression="")
                ]
            )
        )
    )

    response = await service.execute(request, {"application_id": "test"})
    assert response.status.name == "MULTIPLE_CANDIDATES"

@pytest.mark.asyncio
async def test_r7_capability_ambiguity_returns_limitation(r7_service):
    """
    Proof that multiple matching capabilities result in execution limitation, not arbitrary choice.
    """
    request = AbstractEvidenceRequest(
        classified_requirement=ClassifiedRequirement(
            understanding=ConversationalUnderstanding(
                intent="ACTION",
                entities=[
                    ConversationalComponent(identity="inventory.action.receive", operator="EQUALS", value="true", original_expression=""),
                    ConversationalComponent(identity="inventory.action.return", operator="EQUALS", value="true", original_expression=""),
                    ConversationalComponent(identity="inventory.entity.supplier", operator="EQUALS", value=str(uuid.uuid4()), original_expression=""),
                    ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", value=str(uuid.uuid4()), original_expression=""),
                    ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", value=str(uuid.uuid4()), original_expression="")
                ]
            )
        )
    )

    response = await r7_service.execute(request, {"application_id": "test"})
    assert response.status.name == "EXECUTION_LIMITATION"
    assert response.execution_limitations[0].missing_parameter == "capability"

@pytest.mark.asyncio
async def test_r7_domain_exception_becomes_limitation():
    from src.foundation.exceptions.base import ValidationException
    from src.domains.context.dtos.integration_dtos import NormalizedParameter, ParameterDataType
    
    class MockFailingGoodsReceiptService:
        async def create(self, schema, created_by):
            raise ValidationException("Quantity must be greater than 0")

    capability = R7GoodsReceiptCapability(MockFailingGoodsReceiptService())
    
    understanding = ConversationalUnderstanding(
        intent="ACTION",
        entities=[
            ConversationalComponent(identity="inventory.action.receive", operator="EQUALS", value="true", original_expression="")
        ],
        parameters=[
            NormalizedParameter(identity="inventory.numeric.quantity", data_type=ParameterDataType.DECIMAL, value=10)
        ]
    )
    
    resolved_candidates = {
        "inventory.entity.supplier": [CandidateEntity(semantic_reference="supplier", business_id=str(uuid.uuid4()), business_name="S", confidence=1.0)],
        "inventory.entity.sku": [CandidateEntity(semantic_reference="sku", business_id=str(uuid.uuid4()), business_name="S", confidence=1.0)],
        "inventory.entity.warehouse": [CandidateEntity(semantic_reference="wh", business_id=str(uuid.uuid4()), business_name="W", confidence=1.0)]
    }
    
    response = await capability.execute(understanding, resolved_candidates, {"user_id": uuid.uuid4()})
    assert response["status"] == "EXECUTION_LIMITATION"
    assert "Domain validation failed" in response["reason"]

@pytest.mark.asyncio
async def test_r7_unexpected_exception_bubbles_up():
    from src.domains.context.dtos.integration_dtos import NormalizedParameter, ParameterDataType
    
    class MockCrashingGoodsReceiptService:
        async def create(self, schema, created_by):
            raise RuntimeError("Database connection lost")

    capability = R7GoodsReceiptCapability(MockCrashingGoodsReceiptService())
    
    understanding = ConversationalUnderstanding(
        intent="ACTION",
        entities=[
            ConversationalComponent(identity="inventory.action.receive", operator="EQUALS", value="true", original_expression="")
        ],
        parameters=[
            NormalizedParameter(identity="inventory.numeric.quantity", data_type=ParameterDataType.DECIMAL, value=10)
        ]
    )
    
    resolved_candidates = {
        "inventory.entity.supplier": [CandidateEntity(semantic_reference="supplier", business_id=str(uuid.uuid4()), business_name="S", confidence=1.0)],
        "inventory.entity.sku": [CandidateEntity(semantic_reference="sku", business_id=str(uuid.uuid4()), business_name="S", confidence=1.0)],
        "inventory.entity.warehouse": [CandidateEntity(semantic_reference="wh", business_id=str(uuid.uuid4()), business_name="W", confidence=1.0)]
    }
    
    with pytest.raises(RuntimeError) as exc_info:
        await capability.execute(understanding, resolved_candidates, {"user_id": uuid.uuid4()})
    
    assert "Database connection lost" in str(exc_info.value)
