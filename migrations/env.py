import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from src.foundation.configuration import get_settings
from src.foundation.database.models import BaseModel

# Import domain models for Alembic autogenerate
from src.domains.masters.models.company import CompanyModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.product_attribute import ProductAttributeModel
from src.domains.masters.models.category_attribute import CategoryAttributeModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.data_ingestion.models.integration import IntegrationModel
from src.domains.data_ingestion.models.import_job import ImportJobModel
from src.domains.data_ingestion.models.import_file import ImportFileModel
from src.domains.data_ingestion.models.import_record import ImportRecordModel
from src.domains.data_ingestion.models.import_error import ImportErrorModel
from src.domains.data_ingestion.models.import_summary import ImportSummaryModel
from src.domains.operations.models.sales_order import SalesOrderModel, SalesOrderItemModel
from src.domains.operations.models.tax_invoice import TaxInvoiceModel, TaxInvoiceItemModel
from src.domains.operations.models.payment import PaymentModel
from src.domains.operations.models.settlement import SettlementModel
from src.domains.operations.models.lifecycle import CustomerReturnPolicyModel, OrderStateTransitionModel
from src.domains.operations.models.refund import RefundModel
from src.domains.matching.models.job import MatchJobModel
from src.domains.matching.models.relationship import MatchRelationshipModel
from src.domains.matching.models.exception import MatchExceptionModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.inventory.models.exception import InventoryExceptionModel
from src.domains.accounting.models.ledger import LedgerModel
from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
from src.domains.connectors.models.report import DownloadedReportModel

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
