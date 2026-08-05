from dependency_injector import containers, providers
from src.foundation.dependency_injection.container import CoreContainer
from src.domains.masters.dependency_injection import MastersContainer
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer
from src.domains.operations.dependency_injection import OperationsContainer
from src.domains.matching.dependency_injection import MatchingContainer

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
