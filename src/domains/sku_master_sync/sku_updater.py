from sqlalchemy.orm import Session
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.pricing import PricingModel
from src.domains.masters.models.packaging import PackagingModel
from src.domains.masters.models.category import CategoryModel
from src.foundation.enums.status import GenericStatus
import json

class SkuUpdater:
    """
    Handles transactional updates of an existing SKU, Product, Pricing, and Packaging.
    Only mutable fields are updated.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def update(self, db_sku: SKUModel, row: dict, category: CategoryModel) -> SKUModel:
        """
        Updates an existing SKU and its associated models transactionally.
        """
        # Product Update
        db_product = db_sku.product
        if db_product:
            db_product.product_code = row["product_code"]
            db_product.product_name = row["name"]
            if category:
                db_product.category_id = category.id
                
        # SKU Update
        try:
            attr_dict = json.loads(row["attributes_raw"]) if row.get("attributes_raw") else {}
        except Exception:
            attr_dict = {}
        
        db_sku.attribute_values = attr_dict
        
        # Reactivation rule (SKU-011)
        if db_sku.status == GenericStatus.INACTIVE:
            db_sku.status = GenericStatus.ACTIVE
            
        # Pricing Update
        if db_sku.pricing:
            db_sku.pricing.selling_price = row["selling_price"]
            db_sku.pricing.mrp = row["mrp"]
            db_sku.pricing.cost_price = row["cost_price"]
            db_sku.pricing.gst_percentage = row["gst_percentage"]
        else:
            if any([row["selling_price"], row["mrp"], row["cost_price"]]):
                pricing = PricingModel(
                    sku_id=db_sku.id,
                    selling_price=row["selling_price"],
                    mrp=row["mrp"],
                    cost_price=row["cost_price"],
                    gst_percentage=row["gst_percentage"]
                )
                self.db.add(pricing)
                
        # Packaging Update
        if db_sku.packaging:
            db_sku.packaging.length = row["length"]
            db_sku.packaging.breadth = row["breadth"]
            db_sku.packaging.height = row["height"]
            db_sku.packaging.weight = row["weight"]
        else:
            if any([row["length"], row["breadth"], row["height"], row["weight"]]):
                packaging = PackagingModel(
                    sku_id=db_sku.id,
                    length=row["length"],
                    breadth=row["breadth"],
                    height=row["height"],
                    weight=row["weight"]
                )
                self.db.add(packaging)
                
        return db_sku
