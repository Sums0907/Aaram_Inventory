from sqlalchemy.orm import Session
from src.domains.masters.models.sku import SKUModel
from src.foundation.enums.status import GenericStatus

class SkuArchiver:
    """
    Handles marking missing SKUs as INACTIVE.
    Enforces the rule that SKUs are never deleted.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def archive(self, db_sku: SKUModel) -> SKUModel:
        """
        Marks an SKU as INACTIVE transactionally.
        """
        db_sku.status = GenericStatus.INACTIVE
        return db_sku
