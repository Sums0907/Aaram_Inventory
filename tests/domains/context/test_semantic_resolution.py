import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domains.context.engine import ContextEngine
from src.domains.context.contracts import (
    ContextCapabilityRequest, ResolvedSemanticRequirement, OriginalRequirement,
    SemanticConstraint, ContextCapabilityResult, ResolutionStatus, EntityResolutionResult
)
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.context.semantic_resolvers import SemanticResolverRegistry, SKUSemanticResolver, SemanticResolver

class MockTargetHandler(BaseCapabilityHandler):
    def __init__(self, target_params):
        self.target_params = target_params

    def get_target_parameters(self) -> dict[str, str]:
        return self.target_params

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        # Check constraints
        return ContextCapabilityResult(status="SUCCESS", data={"constraints": request.requirement.semantic_constraints})

class MockResolver(SemanticResolver):
    def __init__(self, side_effect=None, return_value=None):
        self.side_effect = side_effect
        self.return_value = return_value
        self.calls = []

    async def resolve(self, semantic_value, target_type):
        self.calls.append((semantic_value, target_type))
        if self.side_effect:
            return self.side_effect(semantic_value, target_type)
        return self.return_value

@pytest.fixture
def base_request():
    return ContextCapabilityRequest(
        capability_urn="urn:test",
        requirement=ResolvedSemanticRequirement(
            requirement_id="1",
            original_requirement=OriginalRequirement(semantic_intent="test"),
            core_identities=[],
            semantic_constraints=[]
        )
    )

@pytest.mark.asyncio
async def test_already_target_compatible_value(base_request):
    """A. Already target-compatible value."""
    # Given a UUID for a constraint that needs a UUID
    test_uuid = str(uuid.uuid4())
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value=test_uuid)
    ]
    
    mock_resolver = MockResolver()
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_resolver,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.sku": "UUID"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "SUCCESS"
    assert len(mock_resolver.calls) == 0 # Resolver should not be called

@pytest.mark.asyncio
async def test_semantic_sku_resolution(base_request):
    """B. Semantic SKU resolution."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value="KD-MDB")
    ]
    test_uuid = str(uuid.uuid4())
    
    mock_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.sku",
        original_value="KD-MDB",
        resolved_value=test_uuid,
        target_type="UUID"
    ))
    
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_resolver,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.sku": "UUID"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "SUCCESS"
    assert len(mock_resolver.calls) == 1
    
    # I. Original semantic value remains preserved/auditable.
    constraint = res.data["constraints"][0]
    assert constraint.resolution.status == ResolutionStatus.RESOLVED
    assert constraint.resolution.original_value == "KD-MDB"
    assert constraint.resolution.resolved_value == test_uuid

@pytest.mark.asyncio
async def test_not_found(base_request):
    """C. NOT_FOUND."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value="KD-MDB")
    ]
    mock_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.NOT_FOUND,
        semantic_identity="inventory.entity.sku",
        original_value="KD-MDB",
        target_type="UUID"
    ))
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_resolver,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.sku": "UUID"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "DATA_UNAVAILABLE"
    assert "NOT_FOUND" in res.error_message

@pytest.mark.asyncio
async def test_ambiguous(base_request):
    """D. AMBIGUOUS."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value="KD-MDB")
    ]
    mock_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.AMBIGUOUS,
        semantic_identity="inventory.entity.sku",
        original_value="KD-MDB",
        target_type="UUID"
    ))
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_resolver,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.sku": "UUID"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "ERROR"
    assert "AMBIGUOUS" in res.error_message

@pytest.mark.asyncio
async def test_resolution_unavailable(base_request):
    """E. RESOLUTION_UNAVAILABLE."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value="KD-MDB")
    ]
    mock_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.RESOLUTION_UNAVAILABLE,
        semantic_identity="inventory.entity.sku",
        original_value="KD-MDB",
        target_type="UUID"
    ))
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_resolver,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.sku": "UUID"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "DATA_UNAVAILABLE"

@pytest.mark.asyncio
async def test_invalid_target_representation(base_request):
    """F. Invalid target representation."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value="KD-MDB")
    ]
    mock_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.INVALID,
        semantic_identity="inventory.entity.sku",
        original_value="KD-MDB",
        target_type="INTEGER"
    ))
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_resolver,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.sku": "INTEGER"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "ERROR"
    assert "INVALID" in res.error_message

@pytest.mark.asyncio
async def test_multiple_semantic_identifiers(base_request):
    """G. Multiple semantic identifiers resolving through the registry."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.sku", operator="EQUALS", bound_value="KD-MDB"),
        SemanticConstraint(identity="inventory.entity.warehouse", operator="EQUALS", bound_value="WH-1")
    ]
    
    mock_sku_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.sku",
        original_value="KD-MDB",
        resolved_value=str(uuid.uuid4()),
        target_type="UUID"
    ))
    mock_wh_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.entity.warehouse",
        original_value="WH-1",
        resolved_value=str(uuid.uuid4()),
        target_type="UUID"
    ))
    
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: mock_sku_resolver,
        warehouse_resolver_provider=lambda: mock_wh_resolver,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({
        "inventory.entity.sku": "UUID",
        "inventory.entity.warehouse": "UUID"
    }))
    
    res = await engine.resolve(base_request)
    assert res.status == "SUCCESS"
    assert len(mock_sku_resolver.calls) == 1
    assert len(mock_wh_resolver.calls) == 1

@pytest.mark.asyncio
async def test_target_capability_other_than_uuid(base_request):
    """H. Target capability requiring a representation other than UUID."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.temporal.month", operator="EQUALS", bound_value="January")
    ]
    
    mock_resolver = MockResolver(return_value=EntityResolutionResult(
        status=ResolutionStatus.RESOLVED,
        semantic_identity="inventory.temporal.month",
        original_value="January",
        resolved_value="01",
        target_type="STRING"
    ))
    
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: None,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    registry._resolver_providers["inventory.temporal.month"] = lambda: mock_resolver
    
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.temporal.month": "STRING"}))
    
    res = await engine.resolve(base_request)
    assert res.status == "SUCCESS"
    assert len(mock_resolver.calls) == 1
    assert res.data["constraints"][0].resolution.resolved_value == "01"

@pytest.mark.asyncio
async def test_unregistered_semantic_entity(base_request):
    """L. Ensure an unknown/unregistered semantic entity is handled safely rather than guessed."""
    base_request.requirement.semantic_constraints = [
        SemanticConstraint(identity="inventory.entity.unknown", operator="EQUALS", bound_value="KD-MDB")
    ]
    
    registry = SemanticResolverRegistry(
        sku_resolver_provider=lambda: None,
        warehouse_resolver_provider=lambda: None,
        job_worker_resolver_provider=lambda: None, exception_resolver_provider=lambda: None, supplier_resolver_provider=lambda: None
    )
    engine = ContextEngine(registry)
    engine.register_handler("urn:test", lambda: MockTargetHandler({"inventory.entity.unknown": "UUID"}))
    
    res = await engine.resolve(base_request)
    # The engine should safely skip resolution for unregistered entities (or we could choose to fail).
    # Since we implemented it to just skip if no resolver found:
    assert res.status == "SUCCESS"
    assert not hasattr(res.data["constraints"][0], "resolution") or res.data["constraints"][0].resolution is None

@pytest.mark.asyncio
async def test_sku_semantic_resolver_implementation():
    mock_session = AsyncMock()
    # Mocking rows returned
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("uuid-123",)]
    mock_session.execute.return_value = mock_result
    
    resolver = SKUSemanticResolver(mock_session)
    res = await resolver.resolve("KD-MDB", "UUID")
    
    assert res.status == ResolutionStatus.RESOLVED
    assert res.resolved_value == "uuid-123"
    assert res.target_type == "UUID"
    
    # Test ambiguous
    mock_result.fetchall.return_value = [("uuid-1",), ("uuid-2",)]
    res = await resolver.resolve("KD-MDB", "UUID")
    assert res.status == ResolutionStatus.AMBIGUOUS
    assert res.candidates == ["uuid-1", "uuid-2"]
    
    # Test not found
    mock_result.fetchall.return_value = []
    res = await resolver.resolve("KD-MDB", "UUID")
    assert res.status == ResolutionStatus.NOT_FOUND
    
    # Test invalid target type
    res = await resolver.resolve("KD-MDB", "INTEGER")
    assert res.status == ResolutionStatus.INVALID

from src.domains.context.resolvers.warehouse_resolver import WarehouseSemanticResolver
from src.domains.context.resolvers.job_worker_resolver import JobWorkerSemanticResolver

@pytest.mark.asyncio
async def test_warehouse_semantic_resolver_implementation():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("uuid-wh",)]
    mock_session.execute.return_value = mock_result
    
    resolver = WarehouseSemanticResolver(mock_session)
    res = await resolver.resolve("WH-1", "UUID")
    
    assert res.status == ResolutionStatus.RESOLVED
    assert res.resolved_value == "uuid-wh"
    
    mock_result.fetchall.return_value = []
    res = await resolver.resolve("WH-1", "UUID")
    assert res.status == ResolutionStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_job_worker_semantic_resolver_implementation():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("uuid-jw",)]
    mock_session.execute.return_value = mock_result
    
    resolver = JobWorkerSemanticResolver(mock_session)
    res = await resolver.resolve("Worker-1", "UUID")
    
    assert res.status == ResolutionStatus.RESOLVED
    assert res.resolved_value == "uuid-jw"
    
    mock_result.fetchall.return_value = []
    res = await resolver.resolve("Worker-1", "UUID")
    assert res.status == ResolutionStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_uuid_passthrough_validation():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    # It exists in DB
    mock_result.fetchall.return_value = [("uuid-passthrough",)]
    mock_session.execute.return_value = mock_result
    
    # Test valid UUID passthrough
    test_uuid = str(uuid.uuid4())
    resolver = SKUSemanticResolver(mock_session)
    res = await resolver.resolve(test_uuid, "UUID")
    assert res.status == ResolutionStatus.RESOLVED
    
    # Test invalid UUID format shouldn't crash, should just be treated as string search
    mock_result.fetchall.return_value = []
    res = await resolver.resolve("not-a-uuid", "UUID")
    assert res.status == ResolutionStatus.NOT_FOUND
    
    # Test UUID that doesn't exist in DB (e.g. from another entity)
    mock_result.fetchall.return_value = []
    res = await resolver.resolve(str(uuid.uuid4()), "UUID")
    assert res.status == ResolutionStatus.NOT_FOUND
