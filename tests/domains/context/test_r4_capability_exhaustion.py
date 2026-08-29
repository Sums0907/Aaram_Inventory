import pytest
from src.domains.context.dependency_injection import ContextContainer
from src.domains.context.capabilities import IR4Capability, R4CapabilityRegistry

def test_r4_capability_exhaustion():
    container = ContextContainer()
    
    from unittest.mock import AsyncMock
    container.balance_calculator.override(AsyncMock())
    container.balance_repository.override(AsyncMock())
    container.confidence_engine.override(AsyncMock())
    container.ledger_service.override(AsyncMock())
    container.jobwork_service.override(AsyncMock())
    container.exception_service.override(AsyncMock())
    
    # Initialize capabilities manually for the test to avoid db dependency setup
    registry = container.r4_capability_registry()
    registry.register(container.r4_balance_capability())
    registry.register(container.r4_ledger_capability())
    registry.register(container.r4_jobwork_capability())
    registry.register(container.r4_exception_capability())

    # The Authoritative Census defines the read-only capabilities that belong in R-4.
    authoritative_census = {
        "urn:aarambooks:inventory:capability:balance",
        "urn:aarambooks:inventory:capability:ledger",
        "urn:aarambooks:inventory:capability:jobwork_status",
        "urn:aarambooks:inventory:capability:exception_status"
    }

    registered_urns = set(registry.get_all_urns())
    
    # 1. Assert no capabilities from the authoritative census are missing from the registry
    missing_capabilities = authoritative_census - registered_urns
    assert not missing_capabilities, f"Missing Authoritative R-4 Capabilities in Registry: {missing_capabilities}"

    # 2. Assert no extra capabilities (e.g. R-7 ACTION capabilities) have been accidentally registered
    extra_capabilities = registered_urns - authoritative_census
    assert not extra_capabilities, f"Extra/Invalid Capabilities found in R-4 Registry: {extra_capabilities}. R-7 mutations must NOT be registered here."

    # 3. Assert all capabilities conform to the IR4Capability protocol
    capabilities = registry.get_all_capabilities()
    for cap in capabilities:
        assert hasattr(cap, "supported_intent")
        assert cap.supported_intent in ["RETRIEVE", "DISCOVER"]
        
        # Verify read-only enforcement: fetch_evidence signature must NOT require 'session'
        import inspect
        sig = inspect.signature(cap.fetch_evidence)
        assert "session" not in sig.parameters, f"R-4 Capability {cap.capability_urn} requires a session, violating read-only boundary."
