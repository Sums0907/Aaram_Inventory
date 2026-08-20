from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.category import CategoryModel

class CategoryOwnershipResolver:
    """
    Authoritative service for determining the domain ownership of a category
    using hierarchy traversal, explicitly ignoring the flawed item_type column.
    """
    
    ROOT_DOMAINS = {
        "FG": "FINISHED_GOODS",
        "RM": "OPERATIONAL",
        "PKG": "OPERATIONAL",
        "CON": "OPERATIONAL",
        "AST": "OPERATIONAL",
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(self, category_code: str, memory_cache: Optional[Dict[str, CategoryModel]] = None) -> Dict[str, Any]:
        """
        Traverse the category hierarchy upwards until a root is found.
        Returns a dict:
            {
                "root_code": "...",
                "domain": "...",
                "category_path": "..."
            }
        """
        # We need to fetch the category and its ancestors
        # A simple while loop is safe since depth is usually < 5
        path_codes = []
        
        current_code = category_code
        while True:
            path_codes.append(current_code)
            
            cat = None
            if memory_cache and current_code in memory_cache:
                cat = memory_cache[current_code]
            else:
                stmt = select(CategoryModel).options(selectinload(CategoryModel.parent)).where(CategoryModel.category_code == current_code)
                result = await self.session.execute(stmt)
                cat = result.scalar_one_or_none()
            
            if not cat:
                raise ValueError(f"Category not found in hierarchy: {current_code}")
                
            if not cat.parent_id:
                # Root found
                root_code = cat.category_code
                if root_code not in self.ROOT_DOMAINS:
                    raise ValueError(f"Invalid root ancestor '{root_code}' for category '{category_code}'")
                
                # Reverse path to be Root -> Child
                path_codes.reverse()
                return {
                    "root_code": root_code,
                    "domain": self.ROOT_DOMAINS[root_code],
                    "category_path": "/".join(path_codes)
                }
            
            if cat.parent:
                current_code = cat.parent.category_code
            elif memory_cache and getattr(cat, "parent_id", None):
                # Try to find parent code from memory cache by comparing ID
                parent_id = str(cat.parent_id)
                found = False
                for c_code, c_obj in memory_cache.items():
                    if hasattr(c_obj, "id") and str(c_obj.id) == parent_id:
                        current_code = c_code
                        found = True
                        break
                if not found:
                    raise ValueError(f"Category parent ID {parent_id} not found in DB or memory cache")
            else:
                raise ValueError(f"Category {current_code} has parent_id but no parent loaded")
