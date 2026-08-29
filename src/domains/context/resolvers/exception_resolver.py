from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
from src.domains.inventory.models.exception import InventoryExceptionModel
from src.domains.context.resolvers.base import try_parse_uuid

class ExceptionSemanticResolver:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(self, semantic_value: Any, target_type: str) -> EntityResolutionResult:
        if target_type != "UUID":
            return EntityResolutionResult(
                status=ResolutionStatus.INVALID,
                semantic_identity="inventory.entity.exception",
                original_value=semantic_value,
                target_type=target_type,
                error_reason=f"Target type {target_type} is not supported by Exception resolver"
            )

        val_uuid = try_parse_uuid(semantic_value)
        if val_uuid:
            stmt = select(InventoryExceptionModel.id).where(InventoryExceptionModel.id == val_uuid)
        else:
            val = str(semantic_value)
            stmt = select(InventoryExceptionModel.id).where(
                or_(
                    InventoryExceptionModel.reference_document == val
                )
            )
        
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        
        if len(rows) == 0:
            return EntityResolutionResult(
                status=ResolutionStatus.NOT_FOUND,
                semantic_identity="inventory.entity.exception",
                original_value=semantic_value,
                target_type=target_type,
                resolver_provenance="ExceptionSemanticResolver"
            )
        elif len(rows) > 1:
            return EntityResolutionResult(
                status=ResolutionStatus.AMBIGUOUS,
                semantic_identity="inventory.entity.exception",
                original_value=semantic_value,
                target_type=target_type,
                resolver_provenance="ExceptionSemanticResolver",
                candidates=[str(row[0]) for row in rows]
            )
        else:
            return EntityResolutionResult(
                status=ResolutionStatus.RESOLVED,
                semantic_identity="inventory.entity.exception",
                original_value=semantic_value,
                resolved_value=str(rows[0][0]),
                resolved_type="UUID",
                target_type=target_type,
                resolver_provenance="ExceptionSemanticResolver"
            )
