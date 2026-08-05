from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.operations.models.payment import PaymentModel
from src.domains.operations.schemas.payment import PaymentCreate

class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_payment(self, data: PaymentCreate, created_by: UUID) -> PaymentModel:
        payment_dict = data.model_dump()
        payment_dict["created_by"] = created_by
        payment_dict["updated_by"] = created_by
        
        db_payment = PaymentModel(**payment_dict)
        self.session.add(db_payment)
        await self.session.commit()
        await self.session.refresh(db_payment)
        return db_payment
        
    async def get_by_transaction_id(self, transaction_id: str) -> PaymentModel | None:
        stmt = select(PaymentModel).where(PaymentModel.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
