from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

# -------------------------------------------------------------------------
# Local DTO representation of the public RABTA-CEM Integration Contract.
# These models are strictly for parsing the generic semantic JSON payload
# via FastAPI and must NOT contain routing identifiers or identity context.
# -------------------------------------------------------------------------

class RequirementClass(str, Enum):
    MANDATORY = "MANDATORY"
    OPTIONAL = "OPTIONAL"
    DERIVABLE = "DERIVABLE"
    BROADENABLE = "BROADENABLE"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"

class ParameterDataType(str, Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DATETIME = "DATETIME"
    UUID = "UUID"

class NormalizedParameter(BaseModel):
    identity: str
    data_type: ParameterDataType
    value: Any
    original_expression: str = ""

class ConversationalComponent(BaseModel):
    # Simplified placeholder based on Brain Core expectations
    identity: str
    operator: str
    original_expression: str
    value: Any

class ConversationalUnderstanding(BaseModel):
    intent: str
    entities: List[ConversationalComponent] = []
    conditions: List[ConversationalComponent] = []
    attributes: List[ConversationalComponent] = []
    parameters: List[NormalizedParameter] = []

class ClassifiedComponent(BaseModel):
    component_reference: str
    classification: RequirementClass
    reason: str

class ClassifiedRequirement(BaseModel):
    understanding: ConversationalUnderstanding
    component_classifications: List[ClassifiedComponent] = []
    global_classification: Optional[RequirementClass] = None

class RefinementContext(BaseModel):
    instruction: str
    accepted_candidates: List[str] = []

class AbstractEvidenceRequest(BaseModel):
    classified_requirement: ClassifiedRequirement
    refinement_context: Optional[RefinementContext] = None

class BusinessRealityStatus(str, Enum):
    CAPABILITY_AVAILABLE = "CAPABILITY_AVAILABLE"
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    ENTITY_RESOLVED = "ENTITY_RESOLVED"
    MULTIPLE_CANDIDATES = "MULTIPLE_CANDIDATES"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    EVIDENCE_AVAILABLE = "EVIDENCE_AVAILABLE"
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"
    PARTIAL_EVIDENCE = "PARTIAL_EVIDENCE"
    EXECUTION_LIMITATION = "EXECUTION_LIMITATION"

class CandidateEntity(BaseModel):
    semantic_reference: str
    business_id: str
    business_name: str
    confidence: float

class ExecutionLimitation(BaseModel):
    missing_parameter: str
    reason: str

class BusinessEvidenceResponse(BaseModel):
    status: BusinessRealityStatus
    evidence_data: Optional[Dict[str, Any]] = None
    resolved_candidates: Dict[str, List[CandidateEntity]] = Field(default_factory=dict)
    capabilities_discovered: List[str] = Field(default_factory=list)
    execution_limitations: List[ExecutionLimitation] = Field(default_factory=list)
