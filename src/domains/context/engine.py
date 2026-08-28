import logging
from typing import Dict, Callable
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult
from src.domains.context.handlers.base import BaseCapabilityHandler

logger = logging.getLogger(__name__)

class ContextEngine:
    """
    Blind dispatcher. It maps the incoming capability_urn to a registered handler provider. 
    It performs ZERO semantic resolution, source preference, or NLP planning.
    """
    def __init__(self):
        self._handlers: Dict[str, Callable[[], BaseCapabilityHandler]] = {}

    def register_handler(self, capability_urn: str, handler_provider: Callable[[], BaseCapabilityHandler]):
        self._handlers[capability_urn] = handler_provider

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
            return await handler.handle(request)
        except Exception as e:
            logger.exception(f"Internal error executing capability {urn}: {str(e)}")
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Internal handler fault during capability execution."
            )
