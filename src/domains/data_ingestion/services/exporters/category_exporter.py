from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.services.category_ownership import CategoryOwnershipResolver

class CategoryExporter:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.resolver = CategoryOwnershipResolver(session)

    async def export_data(self, documentation_mode: bool = False) -> List[Dict[str, Any]]:
        # Fetch all categories
        stmt = select(CategoryModel).options(selectinload(CategoryModel.parent))
        result = await self.session.execute(stmt)
        all_cats = result.scalars().all()
        
        # Build memory cache to avoid hitting the DB repeatedly in the resolver
        memory_cache = {c.category_code: c for c in all_cats}
        
        # Filter for OPERATIONAL categories
        operational_cats = []
        for cat in all_cats:
            print(f"DEBUG EXPORTER: cat={cat.category_code}, parent_id={cat.parent_id}")
            try:
                # Resolve domain using the in-memory cache
                resolved = await self.resolver.resolve(cat.category_code, memory_cache=memory_cache)
                if resolved["domain"] == "OPERATIONAL":
                    operational_cats.append(cat)
            except ValueError as e:
                print(f"DEBUG EXCEPTION for {cat.category_code}: {e}")
                # Exclude any categories that don't belong to a known root
                continue
                
        # Build topological sort (parents before children)
        # 1. Map id -> children
        children_map = {}
        for cat in operational_cats:
            pid = str(cat.parent_id) if cat.parent_id else None
            if pid not in children_map:
                children_map[pid] = []
            children_map[pid].append(cat)
            
        print("DEBUG CHILDREN MAP:", {k: [c.category_code for c in v] for k, v in children_map.items()})
            
        # 2. Sort children within map by code for deterministic output
        for pid in children_map:
            children_map[pid].sort(key=lambda x: x.category_code)
            
        # 3. Recursive traversal starting from roots (parent_id is None)
        sorted_cats = []
        
        def traverse(pid):
            print(f"DEBUG TRAVERSE: pid={pid}")
            if pid in children_map:
                for child in children_map[pid]:
                    print(f"DEBUG VISITING: {child.category_code}")
                    sorted_cats.append(child)
                    traverse(str(child.id))
                    
        traverse(None)
        
        # Build export rows
        export_rows = []
        for cat in sorted_cats:
            is_root = cat.parent_id is None
            
            # Restore mode (default) excludes root categories
            if is_root and not documentation_mode:
                continue
                
            row = {
                "Category Code": cat.category_code,
                "Category Name": cat.category_name,
                "Parent Category Code": cat.parent.category_code if cat.parent else "",
                "Description": cat.description or "",
                "Status": cat.status.name,
                "Export Note": "[ROOT - IMMUTABLE - NOT IMPORTABLE]" if is_root else ""
            }
            export_rows.append(row)
            
        return export_rows
