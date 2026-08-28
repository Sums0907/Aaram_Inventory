from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------------------------------
# Inventory-owned transport DTOs implementing the agreed Stage F wire protocol.
# These parse the incoming JSON and serialize the outgoing JSON, remaining 
# completely independent of Brain's Python package structure.
# -------------------------------------------------------------------------

class SemanticConstraint(BaseModel):
    identity: str
    operator: str
    bound_value: Any
    constraint_type: Optional[str] = None # e.g. ENTITY, TEMPORAL

class OriginalRequirement(BaseModel):
    semantic_intent: str

class ResolvedSemanticRequirement(BaseModel):
    requirement_id: str
    original_requirement: OriginalRequirement
    core_identities: List[str]
    semantic_constraints: List[SemanticConstraint]

class ContextCapabilityRequest(BaseModel):
    capability_urn: str
    requirement: ResolvedSemanticRequirement

class ProvenanceMetadata(BaseModel):
    retrieval_timestamp: str
    business_timestamp: str
    derivation_metadata: str

class ContextCapabilityResult(BaseModel):
    status: str  # SUCCESS, DATA_UNAVAILABLE, UNAUTHORIZED, ERROR
    data: Optional[Dict[str, Any]] = None
    provenance_metadata: Optional[ProvenanceMetadata] = None
    error_message: Optional[str] = None
