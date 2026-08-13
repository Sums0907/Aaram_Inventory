from dependency_injector import containers, providers
from src.foundation.dependency_injection.container import CoreContainer
from src.domains.masters.dependency_injection import MastersContainer
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer
from src.domains.operations.dependency_injection import OperationsContainer
from src.domains.matching.dependency_injection import MatchingContainer
from src.domains.inventory.dependency_injection import InventoryContainer
from src.domains.accounting.dependency_injection import AccountingContainer
from src.domains.connectors.container import ConnectorsContainer
from src.app.services.pipeline_orchestrator import PipelineOrchestratorService
from src.app.services.verification import VerificationService

class DomainsContainer(containers.DeclarativeContainer):
    
    core = providers.Container(CoreContainer)

    masters = providers.Container(
        MastersContainer,
        db=core.db,
    )
    inventory = providers.Container(
        InventoryContainer,
        db=core.db
    )
    operations = providers.Container(
        OperationsContainer,
        db=core.db,
        inventory_movement_service=inventory.movement_service
    )
    data_ingestion = providers.Container(
        DataIngestionContainer,
        db=core.db,
        sales_order_service=operations.sales_order_service,
        tax_invoice_service=operations.tax_invoice_service,
        payment_service=operations.payment_service,
        settlement_service=operations.settlement_service
    )
    matching = providers.Container(
        MatchingContainer,
        db=core.db
    )
    accounting = providers.Container(
        AccountingContainer,
        db=core.db
    )

    # Wire expense_service into goods_receipt_service at the cross-domain level
    # (InventoryContainer cannot import AccountingContainer — DomainsContainer bridges them)
    from src.domains.inventory.services.goods_receipt import GoodsReceiptService
    from src.domains.inventory.repositories.goods_receipt import GoodsReceiptRepository
    from src.domains.inventory.services.movement import InventoryMovementService
    from src.domains.inventory.services.transformation_engine import InventoryTransformationEngine
    goods_receipt_service_with_accounting = providers.Factory(
        GoodsReceiptService,
        repository=inventory.provided.goods_receipt_repository.call(),
        movement_service=inventory.provided.movement_service.call(),
        transformation_engine=inventory.provided.transformation_engine.call(),
        expense_service=accounting.provided.jw_expense_service.call(),
    )
    
    connectors = providers.Container(
        ConnectorsContainer,
        db_session=core.db.provided._session_factory.call(),
        import_job_service=data_ingestion.import_job_service
    )
    
    pipeline_orchestrator = providers.Factory(
        PipelineOrchestratorService,
        session=core.db.provided._session_factory.call(),
        matching_engine=matching.engine_service,
        inventory_movement=inventory.movement_service,
        accounting_engine=accounting.engine_service,
        balance_calculator=inventory.balance_calculator
    )
    
    verification_service = providers.Factory(
        VerificationService,
        session=core.db.provided._session_factory.call()
    )
    
    from src.app.services.business_summary import BusinessSummaryService
    business_summary_service = providers.Factory(
        BusinessSummaryService,
        session=core.db.provided._session_factory.call(),
        verification_service=verification_service
    )
