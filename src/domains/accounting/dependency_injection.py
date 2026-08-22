from dependency_injector import containers, providers
from src.domains.accounting.repositories.ledger import LedgerRepository
from src.domains.accounting.repositories.journal import JournalRepository
from src.domains.accounting.services.posting_rule_provider import PostingRuleProvider
from src.domains.accounting.services.engine import AccountingEngineService
from src.domains.accounting.services.aggregation import JournalAggregationService
from src.domains.accounting.services.vyapar_export import VyaparExportService

# Job Worker Accounting sub-domain
from src.domains.accounting.job_worker.repositories.rates import JobWorkRateRepository
from src.domains.accounting.job_worker.repositories.expenses import JobWorkExpenseRepository
from src.domains.accounting.job_worker.repositories.payments import JobWorkerPaymentRepository
from src.domains.accounting.job_worker.repositories.payable import PayableRepository
from src.domains.accounting.job_worker.services.rate_service import RateService
from src.domains.accounting.job_worker.services.expense_service import ExpenseService
from src.domains.accounting.job_worker.services.payment_service import PaymentService
from src.domains.accounting.job_worker.services.payable_service import PayableService


class AccountingContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    ledger_repository = providers.Factory(
        LedgerRepository,
        session=db.provided.scoped_session.call(),
    )
    
    journal_repository = providers.Factory(
        JournalRepository,
        session=db.provided.scoped_session.call(),
    )
    
    journal_aggregation_service = providers.Factory(
        JournalAggregationService,
        session=db.provided.scoped_session.call()
    )
    
    vyapar_export_service = providers.Factory(
        VyaparExportService,
        session=db.provided.scoped_session.call(),
        aggregation_service=journal_aggregation_service
    )
    
    posting_rule_provider = providers.Factory(
        PostingRuleProvider
    )

    engine_service = providers.Factory(
        AccountingEngineService,
        journal_repository=journal_repository,
        ledger_repository=ledger_repository,
        posting_rule_provider=posting_rule_provider
    )

    # -----------------------------------------------------------------------
    # Job Worker Accounting sub-domain
    # -----------------------------------------------------------------------
    jw_rate_repository = providers.Factory(
        JobWorkRateRepository,
        session=db.provided.scoped_session.call(),
    )
    jw_expense_repository = providers.Factory(
        JobWorkExpenseRepository,
        session=db.provided.scoped_session.call(),
    )
    jw_payment_repository = providers.Factory(
        JobWorkerPaymentRepository,
        session=db.provided.scoped_session.call(),
    )
    jw_payable_repository = providers.Factory(
        PayableRepository,
        session=db.provided.scoped_session.call(),
    )

    jw_rate_service = providers.Factory(
        RateService,
        repository=jw_rate_repository,
    )
    jw_expense_service = providers.Factory(
        ExpenseService,
        expense_repository=jw_expense_repository,
        rate_repository=jw_rate_repository,
    )
    jw_payment_service = providers.Factory(
        PaymentService,
        payment_repository=jw_payment_repository,
        expense_repository=jw_expense_repository,
        payable_repository=jw_payable_repository,
    )
    jw_payable_service = providers.Factory(
        PayableService,
        expense_repository=jw_expense_repository,
        payment_repository=jw_payment_repository,
        payable_repository=jw_payable_repository,
    )

