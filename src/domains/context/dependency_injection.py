from dependency_injector import containers, providers
from src.domains.inventory.dependency_injection import InventoryContainer
from src.domains.context.engine import ContextEngine
from src.domains.context.handlers.balance_handler import BalanceCapabilityHandler
from src.domains.context.handlers.ledger_handler import LedgerCapabilityHandler
from src.domains.context.handlers.jobwork_handler import JobworkStatusCapabilityHandler
from src.domains.context.handlers.exception_handler import ExceptionStatusCapabilityHandler
from src.domains.context.semantic_resolvers import SemanticResolverRegistry, SKUSemanticResolver, WarehouseSemanticResolver, JobWorkerSemanticResolver, ExceptionSemanticResolver, SupplierSemanticResolver
from src.domains.context.services.r4_discovery_service import R4DiscoveryService
from src.domains.context.capabilities import (
    R4CapabilityRegistry,
    R4BalanceCapability,
    R4LedgerCapability,
    R4JobworkCapability,
    R4ExceptionCapability
)
from src.domains.context.capabilities.r7_protocol import R7CapabilityRegistry
from src.domains.context.capabilities.r7_action_capabilities import (
    R7GoodsReceiptCapability, R7PurchaseReturnCapability, R7TransformationCapability,
    R7JobWorkIssueCapability, R7JobWorkReturnCapability, R7ExceptionResolutionCapability,
    R7StockAdjustmentCapability
)
from src.domains.context.services.r7_execution_service import R7ExecutionService

class ContextContainer(containers.DeclarativeContainer):
    
    balance_calculator = providers.Dependency()
    ledger_service = providers.Dependency()
    jobwork_service = providers.Dependency()
    exception_service = providers.Dependency()
    db_session = providers.Dependency()
    
    balance_repository = providers.Dependency()
    movement_repository = providers.Dependency()
    confidence_engine = providers.Dependency()
    
    # R-7 Dependencies from Inventory Container
    goods_receipt_service = providers.Dependency()
    purchase_return_service = providers.Dependency()
    transformation_engine = providers.Dependency()
    movement_service = providers.Dependency()

    # R-5 Semantic Resolvers
    sku_semantic_resolver = providers.Factory(
        SKUSemanticResolver,
        session=db_session
    )
    warehouse_semantic_resolver = providers.Factory(
        WarehouseSemanticResolver,
        session=db_session
    )
    job_worker_semantic_resolver = providers.Factory(
        JobWorkerSemanticResolver,
        session=db_session
    )
    exception_semantic_resolver = providers.Factory(
        ExceptionSemanticResolver,
        session=db_session
    )
    supplier_semantic_resolver = providers.Factory(
        SupplierSemanticResolver,
        session=db_session
    )
    
    semantic_resolver_registry = providers.Singleton(
        SemanticResolverRegistry,
        sku_resolver_provider=sku_semantic_resolver.provider,
        warehouse_resolver_provider=warehouse_semantic_resolver.provider,
        job_worker_resolver_provider=job_worker_semantic_resolver.provider,
        exception_resolver_provider=exception_semantic_resolver.provider,
        supplier_resolver_provider=supplier_semantic_resolver.provider
    )
    
    balance_handler = providers.Factory(
        BalanceCapabilityHandler,
        balance_calculator=balance_calculator,
        movement_repository=movement_repository,
        confidence_engine=confidence_engine
    )

    r4_balance_capability = providers.Factory(
        R4BalanceCapability,
        balance_calculator=balance_calculator,
        balance_repository=balance_repository,
        confidence_engine=confidence_engine,
        movement_repository=movement_repository
    )

    r4_ledger_capability = providers.Factory(
        R4LedgerCapability,
        ledger_service=ledger_service
    )

    r4_jobwork_capability = providers.Factory(
        R4JobworkCapability,
        jobwork_service=jobwork_service
    )
    r4_exception_capability = providers.Factory(
        R4ExceptionCapability,
        exception_service=exception_service
    )

    r4_capability_registry = providers.Singleton(R4CapabilityRegistry)

    # R-4 Discovery Service
    r4_discovery_service = providers.Factory(
        R4DiscoveryService,
        semantic_registry=semantic_resolver_registry,
        capability_registry=r4_capability_registry
    )

    # R-7 Capabilities
    r7_goods_receipt_capability = providers.Factory(
        R7GoodsReceiptCapability,
        goods_receipt_service=goods_receipt_service
    )
    r7_purchase_return_capability = providers.Factory(
        R7PurchaseReturnCapability,
        purchase_return_service=purchase_return_service
    )
    r7_transformation_capability = providers.Factory(
        R7TransformationCapability,
        transformation_engine=transformation_engine
    )
    r7_jobwork_issue_capability = providers.Factory(
        R7JobWorkIssueCapability,
        job_work_service=jobwork_service
    )
    r7_jobwork_return_capability = providers.Factory(
        R7JobWorkReturnCapability,
        job_work_service=jobwork_service
    )
    r7_exception_resolution_capability = providers.Factory(
        R7ExceptionResolutionCapability,
        exception_service=exception_service
    )
    r7_stock_adjustment_capability = providers.Factory(
        R7StockAdjustmentCapability,
        movement_service=movement_service
    )

    r7_capability_registry = providers.Singleton(R7CapabilityRegistry)

    r7_execution_service = providers.Factory(
        R7ExecutionService,
        semantic_registry=semantic_resolver_registry,
        capability_registry=r7_capability_registry
    )

    ledger_handler = providers.Factory(
        LedgerCapabilityHandler,
        ledger_service=ledger_service
    )
    
    jobwork_handler = providers.Factory(
        JobworkStatusCapabilityHandler,
        jobwork_service=jobwork_service
    )
    
    exception_handler = providers.Factory(
        ExceptionStatusCapabilityHandler,
        exception_service=exception_service
    )

    # Note: A provider.Singleton returns a single instance of the engine across the app
    context_engine = providers.Singleton(
        ContextEngine,
        semantic_resolver_registry=semantic_resolver_registry
    )

    @staticmethod
    def init_engine(engine: ContextEngine, container: 'ContextContainer'):
        """Registers the configured handlers to the engine on startup using lazy providers"""
        # Pass the provider callables using the providers dictionary to get bound providers without triggering Provide markers
        engine.register_handler("urn:aarambooks:inventory:capability:balance", container.providers["balance_handler"])
        engine.register_handler("urn:aarambooks:inventory:capability:ledger", container.providers["ledger_handler"])
        engine.register_handler("urn:aarambooks:inventory:capability:jobwork_status", container.providers["jobwork_handler"])
        engine.register_handler("urn:aarambooks:inventory:capability:exception_status", container.providers["exception_handler"])

        # Initialize R4CapabilityRegistry
        registry = container.r4_capability_registry()
        registry.register(container.r4_balance_capability())
        registry.register(container.r4_ledger_capability())
        registry.register(container.r4_jobwork_capability())
        registry.register(container.r4_exception_capability())

        # Initialize R7CapabilityRegistry
        r7_registry = container.r7_capability_registry()
        r7_registry.register(container.r7_goods_receipt_capability())
        r7_registry.register(container.r7_purchase_return_capability())
        r7_registry.register(container.r7_transformation_capability())
        r7_registry.register(container.r7_jobwork_issue_capability())
        r7_registry.register(container.r7_jobwork_return_capability())
        r7_registry.register(container.r7_exception_resolution_capability())
        r7_registry.register(container.r7_stock_adjustment_capability())

