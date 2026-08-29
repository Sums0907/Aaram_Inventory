from abc import ABC, abstractmethod
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult

class BaseCapabilityHandler(ABC):
    """
    Base interface for all AaramInventory CEM capability handlers.
    Each handler is responsible for translating generic constraints into physical 
    service calls, executing business rules securely, and returning opaque evidence.
    """
    
    @abstractmethod
    def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        """
        Processes the requirement and returns the result according to Stage F semantics.
        """
        pass

    def get_target_parameters(self) -> dict[str, str]:
        """
        Returns a mapping of semantic constraints (e.g. 'inventory.entity.sku') 
        to their expected physical representation types (e.g. 'UUID').
        """
        return {}
