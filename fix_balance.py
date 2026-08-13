import asyncio
from src.app.container import DomainsContainer
from uuid import UUID

async def main():
    container = DomainsContainer()
    movement_service = container.inventory.movement_service()
    
    warehouse_id = UUID("96c6b20cd1194f97b635c8e5ef87fd52")
    sku_id = UUID("ac6b90f175a142bcb4b7d88d73cbead7")
    
    await movement_service.balance_calculator.recalculate_balance(warehouse_id, sku_id)
    print("Balance recalculated successfully")

asyncio.run(main())
