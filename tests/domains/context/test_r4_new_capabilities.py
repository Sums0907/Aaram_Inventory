import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from src.domains.inventory.services.job_work import JobWorkService
from src.domains.inventory.services.exception import InventoryExceptionService
from src.domains.context.capabilities import R4CapabilityRegistry, R4BalanceCapability, R4LedgerCapability, R4JobworkCapability, R4ExceptionCapability
from src.domains.context.services.r4_discovery_service import R4DiscoveryService
from tests.domains.context.test_r4_discovery_service import create_request, mock_registry, mock_balance_repo, mock_confidence_engine, mock_ledger_service
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
from src.domains.context.dtos.integration_dtos import BusinessRealityStatus, ConversationalComponent

@pytest.fixture
def mock_movement_repo():
    repo = AsyncMock(spec=InventoryMovementRepository)
    repo.get_warehouse_balances.return_value = {}
    return repo

@pytest.fixture
def mock_jobwork_service():
    return AsyncMock(spec=JobWorkService)

@pytest.fixture
def mock_exception_service():
    return AsyncMock(spec=InventoryExceptionService)

@pytest.fixture
def service_with_all(mock_registry, mock_balance_repo, mock_confidence_engine, mock_ledger_service, mock_jobwork_service, mock_exception_service, mock_movement_repo):
    capability_registry = R4CapabilityRegistry()
    capability_registry.register(R4BalanceCapability(
        balance_calculator=AsyncMock(),
        balance_repository=mock_balance_repo,
        confidence_engine=mock_confidence_engine,
        movement_repository=mock_movement_repo
    ))
    capability_registry.register(R4LedgerCapability(
        ledger_service=mock_ledger_service
    ))
    capability_registry.register(R4JobworkCapability(
        jobwork_service=mock_jobwork_service
    ))
    capability_registry.register(R4ExceptionCapability(
        exception_service=mock_exception_service
    ))
    return R4DiscoveryService(
        semantic_registry=mock_registry,
        capability_registry=capability_registry
    )

@pytest.mark.asyncio
async def test_r4_jobwork_applicability_and_evidence(service_with_all, mock_registry, mock_jobwork_service):
    mock_resolver = AsyncMock()
    mock_resolver.resolve.return_value = EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.job_worker",
        original_value="Supplier A",
        target_type="UUID",
        resolved_value=uuid.uuid4(),
        resolved_type="UUID"
    )
    
    def get_resolver_side_effect(identity):
        if identity == "inventory.entity.job_worker":
            return mock_resolver
        return None
        
    mock_registry.get_resolver.side_effect = get_resolver_side_effect
    
    mock_jobwork_service.get_custody_ledger.return_value = [{"some": "ledger"}]
    
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.job_worker", operator="EQUALS", original_expression="Supplier A", value="Supplier A")
    ])
    
    response = await service_with_all.discover(request)
    assert response.status == BusinessRealityStatus.EVIDENCE_AVAILABLE
    assert "jobwork_status" in response.evidence_data
    assert response.evidence_data["jobwork_status"]["custody_ledger"] == [{"some": "ledger"}]
    mock_jobwork_service.get_custody_ledger.assert_called_once()

@pytest.mark.asyncio
async def test_r4_exception_applicability_and_evidence(service_with_all, mock_registry, mock_exception_service):
    mock_resolver = AsyncMock()
    mock_resolver.resolve.return_value = EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.sku",
        original_value="SKU-EXC",
        target_type="UUID",
        resolved_value=uuid.uuid4(),
        resolved_type="UUID"
    )
    
    def get_resolver_side_effect(identity):
        if identity == "inventory.entity.sku":
            return mock_resolver
        return None
        
    mock_registry.get_resolver.side_effect = get_resolver_side_effect
    
    from src.domains.inventory.models.exception import InventoryExceptionModel
    mock_repository = AsyncMock()
    mock_repository.get_open_exceptions_for_sku.return_value = [
        InventoryExceptionModel(
            exception_number="EXC-1",
            exception_date=datetime.now(timezone.utc).date(),
            source_system="Manual",
            expected_quantity=10,
            actual_quantity=8,
            difference=-2,
            status="OPEN"
        )
    ]
    mock_exception_service.repository = mock_repository
    
    request = create_request("RETRIEVE", [
        ConversationalComponent(identity="inventory.entity.sku", operator="EQUALS", original_expression="SKU-EXC", value="SKU-EXC")
    ])
    
    response = await service_with_all.discover(request)
    assert response.status == BusinessRealityStatus.EVIDENCE_AVAILABLE
    assert len(response.capabilities_discovered) == 3
    assert "exception_status" in response.evidence_data
    assert "balance" in response.evidence_data
    assert len(response.evidence_data["exception_status"]["open_exceptions"]) == 1
    mock_exception_service.repository.get_open_exceptions_for_sku.assert_called_once()
