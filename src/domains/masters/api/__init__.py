from fastapi import APIRouter
from .company import router as company_router
from .unit_of_measure import router as uom_router
from .warehouse import router as warehouse_router
from .category import router as category_router
from .product_attribute import router as product_attribute_router
from .product import router as product_router
from .sku import router as sku_router
from .supplier import router as supplier_router
from .inventory_item import router as inventory_item_router
from .hierarchy import router as hierarchy_router

router = APIRouter()
router.include_router(company_router)
router.include_router(uom_router)
router.include_router(warehouse_router)
router.include_router(category_router)
router.include_router(product_attribute_router)
router.include_router(product_router)
router.include_router(sku_router)
router.include_router(supplier_router)
router.include_router(inventory_item_router)
router.include_router(hierarchy_router)
