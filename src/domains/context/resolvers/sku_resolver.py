from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
from src.domains.masters.models.sku import SKUModel
from src.domains.context.resolvers.base import try_parse_uuid

class SKUSemanticResolver:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(self, semantic_value: Any, target_type: str) -> EntityResolutionResult:
        if target_type != "UUID":
            return EntityResolutionResult(
                status=ResolutionStatus.INVALID,
                semantic_identity="inventory.entity.sku",
                original_value=semantic_value,
                target_type=target_type,
                error_reason=f"Target type {target_type} is not supported by SKU resolver"
            )

        val_uuid = try_parse_uuid(semantic_value)
        if val_uuid:
            stmt = select(SKUModel.id).where(SKUModel.id == val_uuid)
        else:
            val = str(semantic_value)
            stmt = select(SKUModel.id).where(
                or_(
                    SKUModel.item_code == val,
                    SKUModel.sku_code == val,
                    SKUModel.shopdeck_sku_id == val,
                    SKUModel.barcode == val
                )
            )
        
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        
        if len(rows) == 0:
            return EntityResolutionResult(
                status=ResolutionStatus.NOT_FOUND,
                semantic_identity="inventory.entity.sku",
                original_value=semantic_value,
                target_type=target_type,
                resolver_provenance="SKUSemanticResolver"
            )
        elif len(rows) > 1:
            return EntityResolutionResult(
                status=ResolutionStatus.AMBIGUOUS,
                semantic_identity="inventory.entity.sku",
                original_value=semantic_value,
                target_type=target_type,
                resolver_provenance="SKUSemanticResolver",
                candidates=[row[0] for row in rows]
            )
        else:
            return EntityResolutionResult(
                status=ResolutionStatus.RESOLVED,
                semantic_identity="inventory.entity.sku",
                original_value=semantic_value,
                resolved_value=rows[0][0],
                resolved_type="UUID",
                target_type=target_type,
                resolver_provenance="SKUSemanticResolver"
            )
