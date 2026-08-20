import pandas as pd
import uuid
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.data_ingestion.services.uom_importer import UOMImporter
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.supplier_importer import SupplierImporter
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.bom_importer import BOMImporter
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.category import CategoryModel

def _clean_df(df: pd.DataFrame) -> List[Dict[str, Any]]:
    df = df.dropna(how="all")
    df = df.fillna("")
    return df.to_dict(orient="records")

async def seed_fg_references(session: AsyncSession, ref_path: str = "tests/data/FG_REFERENCE_CERTIFICATION_DATA.xlsx"):
    ref_df = pd.read_excel(ref_path, sheet_name="Inventory_Items")
    
    fg_root = (await session.execute(select(CategoryModel).where(CategoryModel.category_code == "FG"))).scalars().first()
    if not fg_root:
        return
        
    for _, row in ref_df.iterrows():
        prod_id = uuid.uuid4()
        prod = ProductModel(
            id=prod_id,
            product_code=row["Item Code"],
            product_name=row["Item Name"],
            category_id=fg_root.id,
            status="ACTIVE"
        )
        sku = SKUModel(
            id=uuid.uuid4(),
            item_code=row["Item Code"],
            product_id=prod_id,
            status="ACTIVE"
        )
        
        # In AaramBooks_Master_Data.xlsx, BOM sheet references "SKU-FG", but Inventory_Items uses "ITM-FG".
        # We'll seed the exact item code the BOM needs.
        bom_code_equivalent = str(row["Item Code"]).replace("ITM-", "SKU-")
        sku2 = SKUModel(
            id=uuid.uuid4(),
            item_code=bom_code_equivalent,
            product_id=prod_id,
            status="ACTIVE"
        )
        session.add(prod)
        session.add(sku)
        session.add(sku2)
    await session.flush()

async def import_from_excel(file_path: str, session: AsyncSession) -> dict:
    try:
        xl = pd.ExcelFile(file_path)
    except Exception as e:
        return {"error": str(e)}

    sheets = {sheet: _clean_df(xl.parse(sheet)) for sheet in xl.sheet_names}
    
    results = {}

    if "UoM" in sheets and sheets["UoM"]:
        results["UoM"] = await UOMImporter(session).import_data(sheets["UoM"], is_dry_run=False)

    if "Inventory_Categories" in sheets and sheets["Inventory_Categories"]:
        results["Categories"] = await CategoryImporter(session).import_data(sheets["Inventory_Categories"], is_dry_run=False)

    if "Suppliers" in sheets and sheets["Suppliers"]:
        results["Suppliers"] = await SupplierImporter(session).import_data(sheets["Suppliers"], is_dry_run=False)

    if "Inventory_Items" in sheets and sheets["Inventory_Items"]:
        results["Inventory_Items"] = await ProductSKUImporter(session).import_data(sheets["Inventory_Items"], is_dry_run=False)

    if "BOM" in sheets and sheets["BOM"]:
        results["BOM"] = await BOMImporter(session).import_data(sheets["BOM"], is_dry_run=False)

    await session.flush()
    return results
