import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from src.domains.context.services.r4_discovery_service import R4DiscoveryService
from src.domains.context.capabilities import R4CapabilityRegistry, R4BalanceCapability, R4LedgerCapability
from src.domains.context.dtos.integration_dtos import (
    AbstractEvidenceRequest, ClassifiedRequirement, ConversationalUnderstanding, 
    BusinessRealityStatus, ConversationalComponent
)
from src.domains.context.semantic_resolvers import SemanticResolverRegistry
from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.services.confidence_engine import ConfidenceEngine
from src.domains.inventory.services.ledger_service import InventoryLedgerService
from src.domains.inventory.models.balance import InventoryBalanceModel

@pytest.fixture
def mock_registry():
    registry = MagicMock(spec=SemanticResolverRegistry)
    return registry

@pytest.fixture
def mock_balance_repo():
    return AsyncMock(spec=InventoryBalanceRepository)

@pytest.fixture
def mock_confidence_engine():
    return AsyncMock(spec=ConfidenceEngine)

@pytest.fixture
def mock_ledger_service():
    return AsyncMock(spec=InventoryLedgerService)

@pytest.fixture
def service(mock_registry, mock_balance_repo, mock_confidence_engine, mock_ledger_service):
    capability_registry = R4CapabilityRegistry()
    capability_registry.register(R4BalanceCapability(
        balance_calculator=AsyncMock(),
        balance_repository=mock_balance_repo,
        confidence_engine=mock_confidence_engine
    ))
    capability_registry.register(R4LedgerCapability(
        ledger_service=mock_ledger_service
    ))
    return R4DiscoveryService(
        semantic_registry=mock_registry,
        capability_registry=capability_registry
    )

def create_request(intent: str, entities: list) -> AbstractEvidenceRequest:
    return AbstractEvidenceRequest(
        classified_requirement=ClassifiedRequirement(
            understanding=ConversationalUnderstanding(
                intent=intent,
                entities=entities
            )
        )
    )

@pytest.mark.asyncio
async def test_r4_applicability_unavailable(service):
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.unknown", operator="EQUALS", original_expression="x", value="x")
    ])
    response = await service.discover(request)
    assert response.status == BusinessRealityStatus.CAPABILITY_UNAVAILABLE

@pytest.mark.asyncio
async def test_r4_delegates_to_r5_execution_limitation_missing_warehouse_resolver(service, mock_registry):
    mock_sku_resolver = AsyncMock()
    mock_sku_resolver.resolve.return_value = EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.sku",
        original_value="Blue Bedsheet",
        target_type="UUID",
        resolved_value="uuid-1",
        resolved_type="UUID"
    )
    
    def get_resolver_side_effect(identity):
        if identity == "inventory.entity.sku":
            return mock_sku_resolver
        return None
        
    mock_registry.get_resolver.side_effect = get_resolver_side_effect
    
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", original_expression="Blue", value="Blue"),
        ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", original_expression="Main", value="Main")
    ])
    
    response = await service.discover(request)
    assert response.status == BusinessRealityStatus.EXECUTION_LIMITATION
    assert len(response.execution_limitations) == 1
    assert response.execution_limitations[0].missing_parameter == "inventory.entity.warehouse"

@pytest.mark.asyncio
async def test_r4_multiple_candidates(service, mock_registry):
    mock_resolver = AsyncMock()
    mock_resolver.resolve.return_value = EntityResolutionResult(
        status=ResolutionStatus.AMBIGUOUS,
        semantic_identity="inventory.entity.sku",
        original_value="Blue",
        target_type="UUID",
        candidates=["uuid-1", "uuid-2"]
    )
    
    mock_registry.get_resolver.return_value = mock_resolver
    
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", original_expression="Blue", value="Blue"),
        ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", original_expression="Main", value="Main")
    ])
    
    response = await service.discover(request)
    assert response.status == BusinessRealityStatus.MULTIPLE_CANDIDATES
    assert "inventory.entity.sku" in response.resolved_candidates

@pytest.mark.asyncio
async def test_r4_read_only_evidence_fetching(service, mock_registry, mock_balance_repo, mock_confidence_engine, mock_ledger_service):
    mock_resolver = AsyncMock()
    mock_resolver.resolve.return_value = EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.sku",
        original_value="Val",
        target_type="UUID",
        resolved_value=uuid.uuid4(),
        resolved_type="UUID"
    )
    mock_registry.get_resolver.return_value = mock_resolver
    
    mock_balance_repo.get_balance.return_value = InventoryBalanceModel(
        sku_id=uuid.uuid4(),
        warehouse_id=uuid.uuid4(),
        quantity_on_hand=50,
        confidence_score=99.0,
        last_movement_date=datetime.now(timezone.utc)
    )
    
    confidence_response = MagicMock()
    confidence_response.confidence_score = 99.0
    confidence_response.factors = []
    mock_confidence_engine.calculate_confidence.return_value = confidence_response
    
    from src.domains.inventory.schemas.ledger import InventoryLedgerResponse
    mock_ledger_service.generate_ledger.return_value = InventoryLedgerResponse(
        sku_id=uuid.uuid4(), opening_balance=0,
        entries=[],
        closing_balance=10, generated_at=datetime.now(timezone.utc).date()
    )
    
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", original_expression="S", value="S"),
        ConversationalComponent(identity="inventory.entity.warehouse", operator="EQUALS", original_expression="W", value="W")
    ])
    
    response = await service.discover(request)
    # Both balance and ledger are applicable because both sku and warehouse are present, and ledger requires SKU!
    # Status should be EVIDENCE_AVAILABLE and data should be merged
    assert response.status == BusinessRealityStatus.EVIDENCE_AVAILABLE
    assert len(response.capabilities_discovered) == 2
    assert "balance" in response.evidence_data
    assert "ledger" in response.evidence_data
    assert response.evidence_data["balance"]["total_quantity"] == 50.0

@pytest.mark.asyncio
async def test_r4_ledger_applicability_and_evidence(service, mock_registry, mock_ledger_service):
    mock_resolver = AsyncMock()
    mock_resolver.resolve.return_value = EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.sku",
        original_value="SKU-123",
        target_type="UUID",
        resolved_value=uuid.uuid4(),
        resolved_type="UUID"
    )
    
    mock_registry.get_resolver.return_value = mock_resolver
    
    from src.domains.inventory.schemas.ledger import InventoryLedgerResponse, InventoryLedgerEntry
    from src.domains.inventory.schemas.movement import InventoryMovementResponse
    
    mock_movement = InventoryMovementResponse(
        id=uuid.uuid4(), created_on=datetime.now(timezone.utc), updated_on=datetime.now(timezone.utc),
        created_by=None, updated_by=None, movement_number="M-1", movement_type="PURCHASE_RECEIPT",
        movement_date=datetime.now(timezone.utc).date(), posting_date=datetime(2025, 1, 15).date(),
        status="COMPLETED", warehouse_id=uuid.uuid4(), sku_id=uuid.uuid4(), quantity=10,
        unit_cost=100.0, reference_type="PO", reference_number="PO-1", reference_id=uuid.uuid4()
    )
    
    mock_ledger_service.generate_ledger.return_value = InventoryLedgerResponse(
        sku_id=uuid.uuid4(), opening_balance=0,
        entries=[InventoryLedgerEntry(movement=mock_movement, running_balance=10)],
        closing_balance=10, generated_at=datetime.now(timezone.utc).date()
    )
    
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", original_expression="SKU", value="SKU"),
        ConversationalComponent(identity="inventory.temporal.posting_date", operator="GREATER_THAN", original_expression="2025", value="2025-01-01")
    ])
    
    response = await service.discover(request)
    assert response.status == BusinessRealityStatus.EVIDENCE_AVAILABLE
    assert "ledger" in response.evidence_data
    mock_ledger_service.generate_ledger.assert_called_once()
