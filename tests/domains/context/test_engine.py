import pytest
from src.domains.context.engine import ContextEngine
from src.domains.context.contracts import ContextCapabilityRequest, ResolvedSemanticRequirement, OriginalRequirement, ContextCapabilityResult
from src.domains.context.handlers.base import BaseCapabilityHandler

class MockHandler(BaseCapabilityHandler):
    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        return ContextCapabilityResult(status="SUCCESS", data={"mock": "data"})

class ErrorHandler(BaseCapabilityHandler):
    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        raise ValueError("Simulated fault")

@pytest.mark.asyncio
async def test_engine_dispatches_correctly():
    engine = ContextEngine()
    engine.register_handler("urn:mock:capability", lambda: MockHandler())
    
    req = ContextCapabilityRequest(
        capability_urn="urn:mock:capability",
        requirement=ResolvedSemanticRequirement(
            requirement_id="req-123",
            original_requirement=OriginalRequirement(semantic_intent="do mock"),
            core_identities=[],
            semantic_constraints=[]
        )
    )
    
    res = await engine.resolve(req)
    assert res.status == "SUCCESS"
    assert res.data == {"mock": "data"}

@pytest.mark.asyncio
async def test_engine_handles_unregistered_urn():
    engine = ContextEngine()
    
    req = ContextCapabilityRequest(
        capability_urn="urn:unknown:capability",
        requirement=ResolvedSemanticRequirement(
            requirement_id="req-123",
            original_requirement=OriginalRequirement(semantic_intent="unknown"),
            core_identities=[],
            semantic_constraints=[]
        )
    )
    
    res = await engine.resolve(req)
    assert res.status == "ERROR"
    assert "not support capability URN" in res.error_message

@pytest.mark.asyncio
async def test_engine_catches_handler_exceptions():
    engine = ContextEngine()
    engine.register_handler("urn:error:capability", lambda: ErrorHandler())
    
    req = ContextCapabilityRequest(
        capability_urn="urn:error:capability",
        requirement=ResolvedSemanticRequirement(
            requirement_id="req-123",
            original_requirement=OriginalRequirement(semantic_intent="error"),
            core_identities=[],
            semantic_constraints=[]
        )
    )
    
    res = await engine.resolve(req)
    assert res.status == "ERROR"
    assert "fault" in res.error_message
