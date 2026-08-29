from typing import Callable, Dict, Any, Protocol

from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
from src.domains.context.resolvers.sku_resolver import SKUSemanticResolver
from src.domains.context.resolvers.warehouse_resolver import WarehouseSemanticResolver
from src.domains.context.resolvers.job_worker_resolver import JobWorkerSemanticResolver
from src.domains.context.resolvers.exception_resolver import ExceptionSemanticResolver
from src.domains.context.resolvers.supplier_resolver import SupplierSemanticResolver

class SemanticResolver(Protocol):
    async def resolve(self, semantic_value: Any, target_type: str) -> EntityResolutionResult:
        ...

class SemanticResolverRegistry:
    def __init__(
        self, 
        sku_resolver_provider: Callable[[], SemanticResolver],
        warehouse_resolver_provider: Callable[[], SemanticResolver],
        job_worker_resolver_provider: Callable[[], SemanticResolver],
        exception_resolver_provider: Callable[[], SemanticResolver],
        supplier_resolver_provider: Callable[[], SemanticResolver]
    ):
        self._resolver_providers: Dict[str, Callable[[], SemanticResolver]] = {
            "inventory.entity.sku": sku_resolver_provider,
            "inventory.entity.warehouse": warehouse_resolver_provider,
            "inventory.entity.job_worker": job_worker_resolver_provider,
            "inventory.entity.exception": exception_resolver_provider,
            "inventory.entity.supplier": supplier_resolver_provider
        }

    def get_resolver(self, identity: str) -> SemanticResolver | None:
        provider = self._resolver_providers.get(identity)
        if provider:
            return provider()
        return None
