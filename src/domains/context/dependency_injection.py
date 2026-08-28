from dependency_injector import containers, providers
from src.domains.inventory.dependency_injection import InventoryContainer
from src.domains.context.engine import ContextEngine
from src.domains.context.handlers.balance_handler import BalanceCapabilityHandler
from src.domains.context.handlers.ledger_handler import LedgerCapabilityHandler
from src.domains.context.handlers.jobwork_handler import JobworkStatusCapabilityHandler
from src.domains.context.handlers.exception_handler import ExceptionStatusCapabilityHandler

class ContextContainer(containers.DeclarativeContainer):
    
    balance_calculator = providers.Dependency()
    ledger_service = providers.Dependency()
    jobwork_service = providers.Dependency()
    exception_service = providers.Dependency()

    balance_handler = providers.Factory(
        BalanceCapabilityHandler,
        balance_calculator=balance_calculator
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
        ContextEngine
    )

    @staticmethod
    def init_engine(engine: ContextEngine, container: 'ContextContainer'):
        """Registers the configured handlers to the engine on startup using lazy providers"""
        # Pass the provider callables using the providers dictionary to get bound providers without triggering Provide markers
        engine.register_handler("urn:aarambooks:inventory:capability:balance", container.providers["balance_handler"])
        engine.register_handler("urn:aarambooks:inventory:capability:ledger", container.providers["ledger_handler"])
        engine.register_handler("urn:aarambooks:inventory:capability:jobwork_status", container.providers["jobwork_handler"])
        engine.register_handler("urn:aarambooks:inventory:capability:exception_status", container.providers["exception_handler"])

