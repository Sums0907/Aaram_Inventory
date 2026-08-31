# Phase 1: Design The Generic CEM Resolution Contract

## 1. Structured Resolution Result
To preserve the original semantic value and provide deep auditability, we will introduce `EntityResolutionResult` in `src/domains/context/contracts.py`:

```python
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
```
`SemanticConstraint` will be updated to include an optional `resolution: Optional[EntityResolutionResult] = None`.

## 2. Target Type Mechanism
To prevent UUID assumptions, `BaseCapabilityHandler` will define:
```python
@abstractmethod
def get_target_parameters(self) -> Dict[str, str]:
    # e.g., {"inventory.entity.sku": "UUID", "inventory.entity.warehouse": "UUID"}
    pass
```
The generic `ContextEngine` will call `handler.get_target_parameters()` to determine what the physical handler requires.

## 3. Extensible Registry & Resolver Contract
```python
class SemanticResolver(ABC):
    @abstractmethod
    async def resolve(self, semantic_value: Any, target_type: str) -> EntityResolutionResult:
        pass

class SemanticResolverRegistry:
    def __init__(self):
        self._resolvers: Dict[str, SemanticResolver] = {}

    def register(self, identity: str, resolver: SemanticResolver):
        self._resolvers[identity] = resolver
```

## 4. SKU Entity Resolution (Deterministic)
The `SKUResolver` will query the authoritative `SKUModel` looking across `item_code`, `sku_code`, `shopdeck_sku_id`, and `barcode`.
If `target_type == "UUID"`, it extracts the `id`. 
- `count == 0` -> `NOT_FOUND`
- `count == 1` -> `RESOLVED`
- `count > 1` -> `AMBIGUOUS`

## Verification Against Constraints
- **Brain Core unchanged**: Yes, `ContextCapabilityRequest` structure remains compatible.
- **No Inventory logic in Brain Core**: Yes.
- **No UUID assumption**: Handlers specify their target type; resolver adapts.
- **Original semantic value preserved**: Preserved in `EntityResolutionResult.original_value`.
- **Registry is extensible**: Yes.
- **Resolver outcomes distinguished**: Yes, via `ResolutionStatus`.
- **No LLM-based entity resolution**: Pure SQLAlchemy ORM logic.
- **No database schema invention**: Uses existing `SKUModel`.

## Decision
**PASS**
