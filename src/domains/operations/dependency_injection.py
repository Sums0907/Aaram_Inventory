from src.domains.operations.repositories.sales_order import SalesOrderRepository
from src.domains.operations.services.sales_order import SalesOrderService
from src.domains.operations.repositories.tax_invoice import TaxInvoiceRepository
from src.domains.operations.services.tax_invoice import TaxInvoiceService
from src.domains.operations.repositories.settlement import SettlementRepository
from src.domains.operations.services.settlement import SettlementService
from src.domains.operations.repositories.payment import PaymentRepository
from src.domains.operations.services.payment import PaymentService
from src.domains.operations.repositories.refund import RefundRepository
from src.domains.operations.services.refund import RefundService
from src.domains.operations.services.report_window import ShopDeckReportWindowService, DateProvider
from src.domains.operations.services.lifecycle_engine import LifecycleEngine
from src.domains.operations.services.reconciliation_orchestrator import ReconciliationOrchestratorService

from dependency_injector import containers, providers

class OperationsContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    # Repositories
    sales_order_repository = providers.Factory(
        SalesOrderRepository,
        session=db.provided._session_factory.call(),
    )
    
    tax_invoice_repository = providers.Factory(
        TaxInvoiceRepository,
        session=db.provided._session_factory.call(),
    )
    
    settlement_repository = providers.Factory(
        SettlementRepository,
        session=db.provided._session_factory.call(),
    )
    
    payment_repository = providers.Factory(
        PaymentRepository,
        session=db.provided._session_factory.call(),
    )
    
    refund_repository = providers.Factory(
        RefundRepository,
        session=db.provided._session_factory.call(),
    )

    # Services
    sales_order_service = providers.Factory(
        SalesOrderService,
        repository=sales_order_repository,
    )
    
    tax_invoice_service = providers.Factory(
        TaxInvoiceService,
        repository=tax_invoice_repository,
    )
    
    settlement_service = providers.Factory(
        SettlementService,
        repository=settlement_repository,
    )
    
    payment_service = providers.Factory(
        PaymentService,
        repository=payment_repository,
    )
    
    refund_service = providers.Factory(
        RefundService,
        repository=refund_repository,
    )

    date_provider = providers.Factory(DateProvider)

    report_window_service = providers.Factory(
        ShopDeckReportWindowService,
        session=db.provided._session_factory.call(),
        date_provider=date_provider
    )

    lifecycle_engine = providers.Factory(
        LifecycleEngine,
        session=db.provided._session_factory.call(),
    )

    inventory_movement_service = providers.Dependency()
    
    reconciliation_orchestrator = providers.Factory(
        ReconciliationOrchestratorService,
        session=db.provided._session_factory.call(),
        window_service=report_window_service,
        lifecycle_engine=lifecycle_engine,
        movement_service=inventory_movement_service
    )
