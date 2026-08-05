from dependency_injector import containers, providers
from src.domains.accounting.repositories.ledger import LedgerRepository
from src.domains.accounting.repositories.journal import JournalRepository
from src.domains.accounting.services.posting_rule_provider import PostingRuleProvider
from src.domains.accounting.services.engine import AccountingEngineService

class AccountingContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    ledger_repository = providers.Factory(
        LedgerRepository,
        session=db.provided._session_factory.call(),
    )
    
    journal_repository = providers.Factory(
        JournalRepository,
        session=db.provided._session_factory.call(),
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
