import pytest
import pytest_asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.context.resolvers.supplier_resolver import SupplierSemanticResolver
from src.domains.context.contracts import ResolutionStatus
from src.domains.masters.models.supplier import Supplier
from src.domains.context.semantic_resolvers import SemanticResolverRegistry

@pytest_asyncio.fixture
async def setup_test_data(db_session: AsyncSession):
    # Setup some test suppliers
    s1 = Supplier(id=uuid4(), name="Acme Corp", gstin="29ABCDE1234F1Z5", is_job_worker=False)
    s2 = Supplier(id=uuid4(), name="Globex", gstin="07AAAAA0000A1Z5", is_job_worker=False)
    s3 = Supplier(id=uuid4(), name="Ambiguous Supplier", gstin="33BBBBB1111B1Z5", is_job_worker=False)
    s4 = Supplier(id=uuid4(), name="Ambiguous Supplier", gstin="33BBBBB1111B1Z5", is_job_worker=False) # Duplicate for testing ambiguity
    
    db_session.add_all([s1, s2, s3, s4])
    await db_session.commit()
    
    return {
        "acme": s1,
        "globex": s2,
        "ambiguous1": s3,
        "ambiguous2": s4
    }

@pytest.mark.asyncio
async def test_supplier_resolver_uuid_valid(db_session, setup_test_data):
    resolver = SupplierSemanticResolver(db_session)
    acme_id = setup_test_data["acme"].id
    
    # Try resolving via exact UUID string
    result = await resolver.resolve(str(acme_id), "UUID")
    
    assert result.status == ResolutionStatus.RESOLVED
    assert result.resolved_value == acme_id
    assert result.resolved_type == "UUID"
    assert result.semantic_identity == "inventory.entity.supplier"

@pytest.mark.asyncio
async def test_supplier_resolver_uuid_invalid(db_session):
    resolver = SupplierSemanticResolver(db_session)
    random_id = str(uuid4())
    
    result = await resolver.resolve(random_id, "UUID")
    
    assert result.status == ResolutionStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_supplier_resolver_name(db_session, setup_test_data):
    resolver = SupplierSemanticResolver(db_session)
    
    result = await resolver.resolve("Acme Corp", "UUID")
    
    assert result.status == ResolutionStatus.RESOLVED
    assert result.resolved_value == setup_test_data["acme"].id

@pytest.mark.asyncio
async def test_supplier_resolver_gstin(db_session, setup_test_data):
    resolver = SupplierSemanticResolver(db_session)
    
    result = await resolver.resolve("07AAAAA0000A1Z5", "UUID")
    
    assert result.status == ResolutionStatus.RESOLVED
    assert result.resolved_value == setup_test_data["globex"].id

@pytest.mark.asyncio
async def test_supplier_resolver_not_found(db_session):
    resolver = SupplierSemanticResolver(db_session)
    
    result = await resolver.resolve("Nonexistent Supplier", "UUID")
    
    assert result.status == ResolutionStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_supplier_resolver_ambiguous(db_session, setup_test_data):
    resolver = SupplierSemanticResolver(db_session)
    
    result = await resolver.resolve("Ambiguous Supplier", "UUID")
    
    assert result.status == ResolutionStatus.AMBIGUOUS
    assert result.candidates is not None
    assert len(result.candidates) == 2
    assert setup_test_data["ambiguous1"].id in result.candidates
    assert setup_test_data["ambiguous2"].id in result.candidates

@pytest.mark.asyncio
async def test_supplier_resolver_invalid_target_type(db_session):
    resolver = SupplierSemanticResolver(db_session)
    
    result = await resolver.resolve("Acme Corp", "STRING")
    
    assert result.status == ResolutionStatus.INVALID
    assert result.error_reason is not None

from src.domains.context.dependency_injection import ContextContainer

@pytest.mark.asyncio
async def test_supplier_registry_wiring():
    container = ContextContainer()
    from unittest.mock import AsyncMock
    container.db_session.override(AsyncMock())
    registry: SemanticResolverRegistry = container.semantic_resolver_registry()
    resolver = registry.get_resolver("inventory.entity.supplier")
    
    assert resolver is not None
    assert isinstance(resolver, SupplierSemanticResolver)
