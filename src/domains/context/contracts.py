from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------------------------------
# Inventory-owned transport DTOs implementing the agreed Stage F wire protocol.
# These parse the incoming JSON and serialize the outgoing JSON, remaining 
# completely independent of Brain's Python package structure.
# -------------------------------------------------------------------------

from enum import Enum

class ResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"
    RESOLUTION_UNAVAILABLE = "RESOLUTION_UNAVAILABLE"
    INVALID = "INVALID"

class EntityResolutionResult(BaseModel):
    status: ResolutionStatus
    semantic_identity: str
    original_value: Any
    resolved_value: Optional[Any] = None
    resolved_type: Optional[str] = None
    target_type: str
    resolver_provenance: Optional[str] = None
    candidates: Optional[List[Any]] = None
    error_reason: Optional[str] = None

class SemanticConstraint(BaseModel):
    identity: str
    operator: str
    bound_value: Any
    constraint_type: Optional[str] = None # e.g. ENTITY, TEMPORAL
    resolution: Optional[EntityResolutionResult] = None

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
