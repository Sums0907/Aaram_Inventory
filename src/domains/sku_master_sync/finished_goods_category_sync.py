from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.domains.masters.models.category import CategoryModel

class FinishedGoodsCategorySync:
    """
    Resolves Category Path from ShopDeck and ensures it belongs to FINISHED_GOODS.
    Uses sync db session for the sync engine.
    """
    
    ROOT_DOMAINS = {
        "FG": "FINISHED_GOODS",
        "RM": "OPERATIONAL",
        "PKG": "OPERATIONAL",
        "CON": "OPERATIONAL",
        "AST": "OPERATIONAL",
    }
    
    def __init__(self, db: Session):
        self.db = db
        
    async def resolve(self, category_path: str) -> Optional[CategoryModel]:
        """
        Attempts to resolve a Category by path. 
        If found, validates it belongs to FINISHED_GOODS.
        Returns the category model if valid, None if not found or invalid.
        """
        if not category_path:
            return None
            
        leaf_name = category_path.split("->")[-1].strip() if "->" in category_path else category_path.strip()
        
        stmt = select(CategoryModel).where(CategoryModel.name == leaf_name)
        category = (await self.db.execute(stmt)).scalars().first()
        
        if not category:
            return None
            
        # Synchronous hierarchy traversal
        current_cat = category
        while current_cat.parent_id:
            parent_stmt = select(CategoryModel).where(CategoryModel.id == current_cat.parent_id)
            current_cat = (await self.db.execute(parent_stmt)).scalars().first()
            if not current_cat:
                raise ValueError("Broken category hierarchy")
                
        root_code = current_cat.category_code
        domain = self.ROOT_DOMAINS.get(root_code)
        
        if domain != "FINISHED_GOODS":
            raise ValueError(f"Category '{category_path}' resolved to domain {domain}, expected FINISHED_GOODS.")
            
        return category
