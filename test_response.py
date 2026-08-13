import asyncio
from uuid import uuid4
from datetime import date
from src.domains.accounting.job_worker.schemas.job_work_rate import JobWorkRateResponse
from src.domains.accounting.job_worker.models.job_work_rate import JobWorkRateModel

async def main():
    try:
        model = JobWorkRateModel(
            job_worker_id=uuid4(),
            sku_id=uuid4(),
            rate=10.5,
            rate_basis="PER_PIECE",
            effective_from=date.today(),
            is_active=True,
            notes=None,
            created_by=uuid4(),
            updated_by=uuid4()
        )
        print("Model created.")
        response = JobWorkRateResponse.model_validate(model, from_attributes=True)
        print("Response validated successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
