import asyncio
from src.foundation.database.session import get_session
from src.domains.masters.models.bom import BOMModel
from sqlalchemy import select

async def main():
    async for s in get_session():
        res = await s.execute(select(BOMModel.bom_number, BOMModel.bom_name).limit(5))
        for row in res.all():
            print(row)
        break

if __name__ == "__main__":
    asyncio.run(main())
