from dependency_injector import containers, providers
from src.foundation.dependency_injection.container import CoreContainer
from src.domains.masters.dependency_injection import MastersContainer
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer
from src.domains.operations.dependency_injection import OperationsContainer
from src.domains.matching.dependency_injection import MatchingContainer
from src.domains.inventory.dependency_injection import InventoryContainer
from src.domains.accounting.dependency_injection import AccountingContainer
from src.app.services.pipeline_orchestrator import PipelineOrchestratorService
from src.app.services.verification import VerificationService

class DomainsContainer(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)

    masters = providers.Container(
        MastersContainer,
        db=core.db,
    )
    operations = providers.Container(
        OperationsContainer,
        db=core.db
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
    inventory = providers.Container(
        InventoryContainer,
        db=core.db
    )
    accounting = providers.Container(
        AccountingContainer,
        db=core.db
    )
    
    pipeline_orchestrator = providers.Factory(
        PipelineOrchestratorService,
        session=core.db.provided._session_factory.call(),
        matching_engine=matching.engine_service,
        inventory_movement=inventory.movement_service,
        accounting_engine=accounting.engine_service
    )
    
    verification_service = providers.Factory(
        VerificationService,
        session=core.db.provided._session_factory.call()
    )
