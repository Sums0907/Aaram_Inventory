import asyncio
from sqlalchemy import select
from src.app.container import DomainsContainer
from src.domains.masters.models.category import CategoryModel

async def check_cycles():
    container = DomainsContainer()
    container.core.config.from_dict({
        "DATABASE_URL": "postgresql+asyncpg://inventory:inventory_password@localhost:5432/inventory_prod", 
        "DATABASE_ENV": "production",
        "DB_POOL_SIZE": 5,
        "DB_MAX_OVERFLOW": 10
    })
    
    db = container.core.db()
    async with db._session_factory() as session:
        stmt = select(CategoryModel)
        result = await session.execute(stmt)
        all_cats = result.scalars().all()
        
        children_map = {}
        for cat in all_cats:
            pid = str(cat.parent_id) if cat.parent_id else None
            if pid not in children_map:
                children_map[pid] = []
            children_map[pid].append(cat)
            
        visited = set()
        path = []
        
        def traverse(pid):
            if pid in path:
                print("CYCLE DETECTED!", path, "->", pid)
                return True
            
            if pid in children_map:
                path.append(pid)
                for child in children_map[pid]:
                    if traverse(str(child.id)):
                        return True
                path.pop()
            return False
            
        if traverse(None):
            print("Found a cycle starting from root!")
        else:
            # Check for disconnected components
            for cat in all_cats:
                if str(cat.id) not in visited:
                    if traverse(str(cat.id)):
                        print("Found a cycle in disconnected component!")
                        break
            print("Finished cycle check.")

if __name__ == "__main__":
    asyncio.run(check_cycles())
