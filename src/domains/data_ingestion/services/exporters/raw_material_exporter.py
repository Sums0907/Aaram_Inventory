from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.foundation.enums import ItemType

class RawMaterialExporter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_data(self) -> List[Dict[str, Any]]:
        # Export only products where item_type = 'RAW_MATERIAL'
        stmt = (
            select(SKUModel)
            .join(ProductModel)
            .where(ProductModel.item_type == ItemType.RAW_MATERIAL)
            .options(
                selectinload(SKUModel.product).selectinload(ProductModel.category),
                selectinload(SKUModel.pricing),
                selectinload(SKUModel.packaging),
                selectinload(SKUModel.uom)
            )
            .order_by(SKUModel.item_code)
        )
        result = await self.session.execute(stmt)
        skus = result.scalars().all()
        
        export_rows = []
        for sku in skus:
            prod = sku.product
            pr = sku.pricing
            pa = sku.packaging
            
            export_rows.append({
                "Item Code": sku.item_code,
                "Master Item Name": prod.product_name,
                "Category Code": prod.category.category_code if prod.category else "",
                "Base UoM Code": sku.uom.unit_code if sku.uom else "",
                "Barcode": sku.barcode or "",
                "attr_Brand": prod.brand or "",
                "Size": sku.size or "",
                "Colour": sku.color or "",
                "Description": prod.description or "",
                "Status": sku.status.name,
                
                "Selling Price": float(pr.selling_price) if pr and pr.selling_price else 0.0,
                "MRP": float(pr.mrp) if pr and pr.mrp else 0.0,
                "Cost Price": float(pr.cost_price) if pr and pr.cost_price else 0.0,
                "GST %": float(pr.gst_percentage) if pr and pr.gst_percentage else 0.0,
                "HSN Code": pr.hsn_code if pr and pr.hsn_code else "",
                
                "Packaging Length (in cm)": float(pa.length) if pa and pa.length else 0.0,
                "Packaging Breadth (in cm)": float(pa.breadth) if pa and pa.breadth else 0.0,
                "Packaging Height (in cm)": float(pa.height) if pa and pa.height else 0.0,
                "Packaging Weight (in kg)": float(pa.weight) if pa and pa.weight else 0.0,
            })
            
        return export_rows
