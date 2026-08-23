import asyncio
from enum import Enum
import uuid
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import Enum as SQLAlchemyEnum, Uuid, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ItemType(str, Enum):
    FINISHED_GOODS = "FINISHED_GOODS"

class CatModel(Base):
    __tablename__ = "cats"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_type: Mapped[ItemType] = mapped_column(SQLAlchemyEnum(ItemType, create_type=False), nullable=False)

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        cat = CatModel(item_type="FINISHED_GOODS") # PASSING STRING
        session.add(cat)
        try:
            await session.commit()
            print("Flush successful!")
        except Exception as e:
            print("Flush failed:", type(e), e)

asyncio.run(main())
