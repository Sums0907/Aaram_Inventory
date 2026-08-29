from typing import List, Dict, Any
from src.domains.context.dtos.integration_dtos import (
    AbstractEvidenceRequest, BusinessEvidenceResponse, BusinessRealityStatus, CandidateEntity, ExecutionLimitation
)
from src.domains.context.semantic_resolvers import SemanticResolverRegistry
from src.domains.context.contracts import ResolutionStatus
from src.domains.context.capabilities.r7_protocol import R7CapabilityRegistry

class R7ExecutionService:
    """
    R-7 Business Execution Orchestrator.
    Determines capability applicability, delegates R-5 entity resolution,
    and performs ACTION-only execution via the R-7 Capability Registry.
    """
    def __init__(
        self, 
        semantic_registry: SemanticResolverRegistry,
        capability_registry: R7CapabilityRegistry
    ):
        self.semantic_registry = semantic_registry
        self.capability_registry = capability_registry

    async def execute(self, request: AbstractEvidenceRequest, execution_context: Dict[str, Any]) -> BusinessEvidenceResponse:
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
                execution_limitations=[ExecutionLimitation(missing_parameter="Unknown", reason="No R-7 capability matches the semantic intent provided.")]
            )
            
        if len(applicable_capabilities) > 1:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.EXECUTION_LIMITATION,
                capabilities_discovered=discovered_urns,
                execution_limitations=[ExecutionLimitation(
                    missing_parameter="capability",
                    reason="ACTION execution matched multiple capabilities. R-7 cannot safely guess intent. Refinement required."
                )]
            )
            
        selected_capability = applicable_capabilities[0]
            
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
            
        # Check required semantics after resolution
        for required_semantic in selected_capability.get_required_semantics():
            if required_semantic not in resolved_candidates:
                execution_limitations.append(ExecutionLimitation(
                    missing_parameter=required_semantic,
                    reason=f"Mandatory entity {required_semantic} missing for execution."
                ))
                
        if execution_limitations:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.EXECUTION_LIMITATION,
                capabilities_discovered=discovered_urns,
                execution_limitations=execution_limitations,
                resolved_candidates=resolved_candidates
            )
            
        # 3. Execution
        if understanding.intent != "ACTION":
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.CAPABILITY_AVAILABLE,
                capabilities_discovered=discovered_urns,
                resolved_candidates=resolved_candidates
            )
            
        try:
            evidence = await selected_capability.execute(understanding, resolved_candidates, execution_context)
            if evidence.get("status") == "PENDING_IMPLEMENTATION":
                return BusinessEvidenceResponse(
                    status=BusinessRealityStatus.CAPABILITY_AVAILABLE,
                    capabilities_discovered=discovered_urns,
                    resolved_candidates=resolved_candidates,
                    execution_limitations=[ExecutionLimitation(
                        missing_parameter="implementation",
                        reason=evidence.get("reason", "Pending")
                    )]
                )
            
            if evidence.get("status") == "EXECUTION_LIMITATION":
                return BusinessEvidenceResponse(
                    status=BusinessRealityStatus.EXECUTION_LIMITATION,
                    capabilities_discovered=discovered_urns,
                    resolved_candidates=resolved_candidates,
                    execution_limitations=[ExecutionLimitation(
                        missing_parameter="capability_execution",
                        reason=evidence.get("reason", "Unknown limitation")
                    )]
                )
            
            # Namespace by capability suffix
            namespace = selected_capability.capability_urn.split(":")[-1]
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.EVIDENCE_AVAILABLE,
                capabilities_discovered=discovered_urns,
                resolved_candidates=resolved_candidates,
                evidence_data={namespace: evidence}
            )
        except Exception as e:
            return BusinessEvidenceResponse(
                status=BusinessRealityStatus.EVIDENCE_UNAVAILABLE,
                capabilities_discovered=discovered_urns,
                execution_limitations=[ExecutionLimitation(missing_parameter="Internal", reason=str(e))]
            )
