from src.domains.data_ingestion.repositories.integration import IntegrationRepository
from src.domains.data_ingestion.repositories.import_job import ImportJobRepository
from src.domains.data_ingestion.repositories.import_file import ImportFileRepository
from src.domains.data_ingestion.repositories.import_record import ImportRecordRepository
from src.domains.data_ingestion.repositories.import_error import ImportErrorRepository
from src.domains.data_ingestion.repositories.import_summary import ImportSummaryRepository
from src.domains.data_ingestion.services.integration import IntegrationService
from src.domains.data_ingestion.services.import_job import ImportJobService
from src.domains.data_ingestion.services.import_file import ImportFileService
from src.domains.data_ingestion.services.import_record import ImportRecordService
from src.domains.data_ingestion.services.import_error import ImportErrorService
from src.domains.data_ingestion.services.import_summary import ImportSummaryService
from src.domains.data_ingestion.services.commit import CommitService
from src.domains.data_ingestion.services.master_data_application_service import MasterDataApplicationService
from src.domains.data_ingestion.services.adapters.shopdeck_order import ShopDeckOrderAdapter
from src.domains.data_ingestion.services.adapters.shopdeck_tax import ShopDeckTaxAdapter
from src.domains.data_ingestion.services.adapters.shopdeck_cod_settlement import ShopDeckCODSettlementAdapter
from src.domains.data_ingestion.services.adapters.razorpay_settlement import RazorpaySettlementAdapter
from src.domains.operations.dependency_injection import OperationsContainer

from dependency_injector import containers, providers

class DataIngestionContainer(containers.DeclarativeContainer):
    db = providers.Dependency()
    
    # External Dependencies
    sales_order_service = providers.Dependency()
    tax_invoice_service = providers.Dependency()
    payment_service = providers.Dependency()
    settlement_service = providers.Dependency()

    # Repositories
    integration_repository = providers.Factory(
        IntegrationRepository,
        session=db.provided._session_factory.call(),
    )
    import_job_repository = providers.Factory(
        ImportJobRepository,
        session=db.provided._session_factory.call(),
    )
    import_file_repository = providers.Factory(
        ImportFileRepository,
        session=db.provided._session_factory.call(),
    )
    import_record_repository = providers.Factory(
        ImportRecordRepository,
        session=db.provided._session_factory.call(),
    )
    import_error_repository = providers.Factory(
        ImportErrorRepository,
        session=db.provided._session_factory.call(),
    )
    import_summary_repository = providers.Factory(
        ImportSummaryRepository,
        session=db.provided._session_factory.call(),
    )

    # Services
    integration_service = providers.Factory(
        IntegrationService,
        repository=integration_repository,
    )
    import_job_service = providers.Factory(
        ImportJobService,
        repository=import_job_repository,
    )
    import_file_service = providers.Factory(
        ImportFileService,
        repository=import_file_repository,
    )
    import_record_service = providers.Factory(
        ImportRecordService,
        repository=import_record_repository,
    )
    import_error_service = providers.Factory(
        ImportErrorService,
        repository=import_error_repository,
    )
    import_summary_service = providers.Factory(
        ImportSummaryService,
        repository=import_summary_repository,
    )
    commit_service = providers.Factory(
        CommitService,
        record_repository=import_record_repository,
        job_repository=import_job_repository,
        summary_service=import_summary_service,
        sales_order_service=sales_order_service,
        tax_invoice_service=tax_invoice_service,
        payment_service=payment_service,
        settlement_service=settlement_service,
    )
    
    master_data_application_service = providers.Factory(
        MasterDataApplicationService,
        session=db.provided._session_factory.call(),
    )
    
    shopdeck_order_adapter = providers.Factory(
        ShopDeckOrderAdapter,
        record_service=import_record_service,
        error_service=import_error_service,
        summary_service=import_summary_service,
    )
    
    shopdeck_tax_adapter = providers.Factory(
        ShopDeckTaxAdapter,
        record_service=import_record_service,
        error_service=import_error_service,
        summary_service=import_summary_service,
    )
    
    shopdeck_cod_settlement_adapter = providers.Factory(
        ShopDeckCODSettlementAdapter,
        record_service=import_record_service,
        error_service=import_error_service,
        summary_service=import_summary_service,
    )
    
    razorpay_settlement_adapter = providers.Factory(
        RazorpaySettlementAdapter,
        record_service=import_record_service,
        error_service=import_error_service,
        summary_service=import_summary_service,
    )
