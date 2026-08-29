from typing import List, Dict, Any
from src.domains.context.dtos.integration_dtos import (
    AbstractEvidenceRequest, BusinessEvidenceResponse, BusinessRealityStatus, CandidateEntity, ExecutionLimitation
)
from src.domains.context.semantic_resolvers import SemanticResolverRegistry
from src.domains.context.contracts import ResolutionStatus
from src.domains.context.capabilities import R4CapabilityRegistry

class R4DiscoveryService:
    """
    R-4 Business Discovery Orchestrator.
    Determines capability applicability, delegates R-5 entity resolution,
    and fetches purely read-only evidence via the Capability Registry.
    """
    def __init__(
        self, 
        semantic_registry: SemanticResolverRegistry,
        capability_registry: R4CapabilityRegistry
    ):
        self.semantic_registry = semantic_registry
        self.capability_registry = capability_registry

    async def discover(self, request: AbstractEvidenceRequest) -> BusinessEvidenceResponse:
        understanding = request.classified_requirement.understanding
        
        # 1. Applicability Check (Discovery)
        applicable_capabilities = []
        for capability in self.capability_registry.get_all_capabilities():
            if capability.is_applicable(understanding):
                applicable_capabilities.append(capability)
                
        discovered_urns = [cap.capability_urn for cap in applicable_capabilities]
        
        if not applicable_capabilities:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.CAPABILITY_UNAVAILABLE,
                execution_limitations=[ExecutionLimitation(missing_parameter="Unknown", reason="No capability matches the semantic entities provided.")]
            )
            
        # 2. R-5 Entity Resolution Delegation
        resolved_candidates: Dict[str, List[CandidateEntity]] = {}
        has_ambiguity = False
        has_not_found = False
        execution_limitations = []
        
        for entity in understanding.entities:
            # Temporal boundaries are structurally consumed by capabilities; they do not need R-5 UUID resolution
            if entity.identity.startswith("inventory.temporal."):
                continue
                
            resolver = self.semantic_registry.get_resolver(entity.identity)
            
            if not resolver:
                execution_limitations.append(ExecutionLimitation(
                    missing_parameter=entity.identity, 
                    reason=f"No R-5 semantic resolver available for {entity.identity}"
                ))
                continue
                
            resolution = await resolver.resolve(entity.value, "UUID")
            
            if resolution.status == ResolutionStatus.AMBIGUOUS:
                has_ambiguity = True
                resolved_candidates[entity.identity] = [
                    CandidateEntity(
                        semantic_reference=str(entity.value),
                        business_id=str(candidate_id),
                        business_name="Candidate (Requires R-6 Refinement)",
                        confidence=0.5
                    ) for candidate_id in (resolution.candidates or [])
                ]
            elif resolution.status == ResolutionStatus.NOT_FOUND:
                has_not_found = True
            elif resolution.status == ResolutionStatus.RESOLVED:
                resolved_candidates[entity.identity] = [
                    CandidateEntity(
                        semantic_reference=str(entity.value),
                        business_id=str(resolution.resolved_value),
                        business_name="Resolved Entity",
                        confidence=1.0
                    )
                ]
        
        if execution_limitations:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.EXECUTION_LIMITATION,
                capabilities_discovered=discovered_urns,
                execution_limitations=execution_limitations,
                resolved_candidates=resolved_candidates
            )
            
        if has_ambiguity:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.MULTIPLE_CANDIDATES,
                capabilities_discovered=discovered_urns,
                resolved_candidates=resolved_candidates
            )
            
        if has_not_found:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.ENTITY_NOT_FOUND,
                capabilities_discovered=discovered_urns
            )
            
        # 3. Capability Selection and Execution
        if understanding.intent != "RETRIEVE":
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.CAPABILITY_AVAILABLE,
                capabilities_discovered=discovered_urns,
                resolved_candidates=resolved_candidates
            )
            
        merged_evidence = {}
        pending_reasons = []
        internal_errors = []
        
        for capability in applicable_capabilities:
            try:
                evidence = await capability.fetch_evidence(understanding, resolved_candidates)
                if evidence.get("status") == "PENDING_IMPLEMENTATION":
                    pending_reasons.append(evidence.get("reason", "Pending"))
                    continue
                
                # Namespace by capability suffix (e.g. "urn:...:capability:balance" -> "balance")
                namespace = capability.capability_urn.split(":")[-1]
                merged_evidence[namespace] = evidence
            except Exception as e:
                internal_errors.append(str(e))
                
        if internal_errors:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.EVIDENCE_UNAVAILABLE,
                capabilities_discovered=discovered_urns,
                execution_limitations=[ExecutionLimitation(missing_parameter="Internal", reason=err) for err in internal_errors]
            )
            
        if pending_reasons and not merged_evidence:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.CAPABILITY_AVAILABLE,
                capabilities_discovered=discovered_urns,
                resolved_candidates=resolved_candidates,
                execution_limitations=[ExecutionLimitation(
                    missing_parameter="implementation",
                    reason=pending_reasons[0]
                )]
            )
            
        return BusinessEvidenceResponse(
            status=BusinessRealityStatus.EVIDENCE_AVAILABLE,
            capabilities_discovered=discovered_urns,
            resolved_candidates=resolved_candidates,
            evidence_data=merged_evidence
        )
