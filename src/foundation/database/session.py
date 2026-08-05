from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

class Database:
    def __init__(self, db_url: str, debug: bool, pool_size: int, max_overflow: int):
        engine_kwargs = {"echo": debug}
        if not db_url.startswith("sqlite"):
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = max_overflow

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

    async def session(self) -> AsyncSession:
        async with self._session_factory() as session:
            yield session

Base = declarative_base()
