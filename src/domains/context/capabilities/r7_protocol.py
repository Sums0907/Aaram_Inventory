from typing import Protocol, Dict, Any, List, Optional
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity

class IR7Capability(Protocol):
    @property
    def capability_urn(self) -> str:
        """The globally unique identifier for this capability."""
        ...

    @property
    def supported_intent(self) -> str:
        """The primary intent this capability fulfills (e.g., ACTION)."""
        return "ACTION"

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        """Predicate determining if the conversational understanding mathematically satisfies this capability's requirements."""
        ...

    def get_required_semantics(self) -> List[str]:
        """Returns the semantic entity constraints mandatory for execution."""
        ...

    async def execute(
        self, 
        understanding: ConversationalUnderstanding, 
        resolved_candidates: Dict[str, List[CandidateEntity]],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executes the state-changing action via the authoritative domain service."""
        ...

class R7CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, IR7Capability] = {}

    def register(self, capability: IR7Capability) -> None:
        if capability.capability_urn in self._capabilities:
            raise ValueError(f"Capability URN {capability.capability_urn} is already registered.")
        self._capabilities[capability.capability_urn] = capability

    def get_all_urns(self) -> List[str]:
        return list(self._capabilities.keys())

    def get_all_capabilities(self) -> List[IR7Capability]:
        return list(self._capabilities.values())
