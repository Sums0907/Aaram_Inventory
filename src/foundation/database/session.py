from asyncio import current_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session
from sqlalchemy.orm import declarative_base
from src.foundation.logging.context import get_request_id
class Database:
    def __init__(self, db_url: str, debug: bool, pool_size: int, max_overflow: int):
        engine_kwargs = {"echo": debug}
        if not db_url.startswith("sqlite"):
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = max_overflow
            engine_kwargs["pool_pre_ping"] = True   # Detect and discard stale/zombie connections
            engine_kwargs["pool_recycle"] = 1800    # Recycle connections after 30 minutes
            engine_kwargs["pool_timeout"] = 10      # Fail fast (10s) instead of hanging for 30s

        self._engine = create_async_engine(
            db_url,
            **engine_kwargs
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        # Scoped session: one session per HTTP request (via Request ID ContextVar).
        # We use `get_request_id` instead of `current_task` because Starlette's BaseHTTPMiddleware 
        # executes `call_next` in a different asyncio Task, which would leak connections.
        self.scoped_session = async_scoped_session(
            self._session_factory,
            scopefunc=get_request_id,
        )

    async def session(self) -> AsyncSession:
        async with self._session_factory() as session:
            yield session

Base = declarative_base()

from sqlalchemy import event, Delete
from sqlalchemy.schema import MetaData
from sqlalchemy.engine import Engine
from src.foundation.database.safety import assert_destructive_operation_allowed

@event.listens_for(MetaData, "before_drop")
def protect_database_drop(target, connection, **kw):
    # Retrieve the engine URL directly from the connection
    url = str(connection.engine.url)
    assert_destructive_operation_allowed("DROP ALL TABLES", url)

@event.listens_for(Engine, "before_execute")
def protect_database_execute(conn, clauseelement, multiparams, params, execution_options):
    if isinstance(clauseelement, Delete):
        # Block ALL raw bulk deletes via execution (including DELETE ... WHERE)
        # Normal CRUD (session.delete) will not be intercepted here
        url = str(conn.engine.url)
        assert_destructive_operation_allowed("EXPLICIT BULK DELETE (session.execute(delete(...)))", url)
