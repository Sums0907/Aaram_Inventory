from sqlalchemy.orm import Session
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.pricing import PricingModel
from src.domains.masters.models.packaging import PackagingModel
from src.domains.masters.models.category import CategoryModel
from src.foundation.enums.item_type import ItemType
from src.foundation.enums.status import GenericStatus
import uuid
import json

class SkuCreator:
    """
    Handles transactional creation of a new SKU, Product, Pricing, and Packaging.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def create(self, row: dict, category: CategoryModel) -> SKUModel:
        """
        Creates a new SKU with all associated models transactionally.
        """
        # Product
        product = ProductModel(
            product_code=row["product_code"],
            product_name=row["name"],
            item_type=ItemType.FINISHED_GOODS,
            status=GenericStatus.ACTIVE,
            category_id=category.id if category else None
        )
        self.db.add(product)
        await self.db.flush() # get product.id
        
        # Parse attributes
        try:
            attr_dict = json.loads(row["attributes_raw"]) if row.get("attributes_raw") else {}
        except Exception:
            attr_dict = {}
            
        # Generate internal item code
        internal_item_code = f"FG-{uuid.uuid4().hex[:8].upper()}"
        
        # SKU
        sku = SKUModel(
            item_code=internal_item_code,
            shopdeck_sku_id=row["shopdeck_sku_id"],
            product_id=product.id,
            status=GenericStatus.ACTIVE,
            attribute_values=attr_dict
        )
        self.db.add(sku)
        await self.db.flush() # get sku.id
        
        # Pricing
        pricing = PricingModel(
            sku_id=sku.id,
            selling_price=row["selling_price"],
            mrp=row["mrp"],
            cost_price=row["cost_price"],
            gst_percentage=row["gst_percentage"]
        )
        self.db.add(pricing)
        
        # Packaging
        packaging = PackagingModel(
            sku_id=sku.id,
            length=row["length"],
            breadth=row["breadth"],
            height=row["height"],
            weight=row["weight"]
        )
        self.db.add(packaging)
        
        return sku
