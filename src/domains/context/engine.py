import logging
import uuid
from typing import Dict, Callable
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.context.semantic_resolvers import SemanticResolverRegistry
from src.domains.context.contracts import ResolutionStatus

logger = logging.getLogger(__name__)

class ContextEngine:
    """
    Blind dispatcher that now includes semantic entity resolution.
    It resolves semantic constraints into target types defined by the capability handler
    before executing the handler.
    """
    def __init__(self, semantic_resolver_registry: SemanticResolverRegistry = None):
        self._handlers: Dict[str, Callable[[], BaseCapabilityHandler]] = {}
        self.registry = semantic_resolver_registry

    def register_handler(self, capability_urn: str, handler_provider: Callable[[], BaseCapabilityHandler]):
        self._handlers[capability_urn] = handler_provider

    def _is_uuid(self, val: str) -> bool:
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    async def resolve(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        urn = request.capability_urn
        handler_provider = self._handlers.get(urn)
        
        if not handler_provider:
            logger.warning(f"No handler registered for capability URN: {urn}")
            return ContextCapabilityResult(
                status="ERROR",
                error_message=f"AaramInventory does not support capability URN: {urn}"
            )
            
        try:
            handler = handler_provider()
            
            # Phase 1: Pre-process constraints
            if self.registry:
                target_params = handler.get_target_parameters()
                for constraint in request.requirement.semantic_constraints:
                    target_type = target_params.get(constraint.identity)
                    
                    if target_type and not self._is_uuid(constraint.bound_value):
                        resolver = self.registry.get_resolver(constraint.identity)
                        if resolver:
                            resolution = await resolver.resolve(constraint.bound_value, target_type)
                            constraint.resolution = resolution
                            if resolution.status != ResolutionStatus.RESOLVED:
                                return ContextCapabilityResult(
                                    status="DATA_UNAVAILABLE" if resolution.status in [ResolutionStatus.NOT_FOUND, ResolutionStatus.RESOLUTION_UNAVAILABLE] else "ERROR",
                                    error_message=f"Semantic resolution failed for {constraint.identity}: {resolution.status.value}"
                                )

            # Phase 2: Execute handler
            return await handler.handle(request)
        except Exception as e:
            logger.exception(f"Internal error executing capability {urn}: {str(e)}")
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Internal handler fault during capability execution."
            )
