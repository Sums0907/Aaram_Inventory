from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.domains.context.contracts import EntityResolutionResult, ResolutionStatus
from src.domains.masters.models.supplier import Supplier
from src.domains.context.resolvers.base import try_parse_uuid

class JobWorkerSemanticResolver:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(self, semantic_value: Any, target_type: str) -> EntityResolutionResult:
        if target_type != "UUID":
            return EntityResolutionResult(
                status=ResolutionStatus.INVALID,
                semantic_identity="inventory.entity.job_worker",
                original_value=semantic_value,
                target_type=target_type,
                error_reason=f"Target type {target_type} is not supported by JobWorker resolver"
            )

        val_uuid = try_parse_uuid(semantic_value)
        if val_uuid:
            stmt = select(Supplier.id).where(
                Supplier.id == val_uuid,
                Supplier.is_job_worker == True
            )
        else:
            val = str(semantic_value)
            stmt = select(Supplier.id).where(
                or_(
                    Supplier.name == val,
                    Supplier.gstin == val
                ),
                Supplier.is_job_worker == True
            )
        
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        
        if len(rows) == 0:
            return EntityResolutionResult(
                status=ResolutionStatus.NOT_FOUND,
                semantic_identity="inventory.entity.job_worker",
                original_value=semantic_value,
                target_type=target_type,
                resolver_provenance="JobWorkerSemanticResolver"
            )
        elif len(rows) > 1:
            return EntityResolutionResult(
                status=ResolutionStatus.AMBIGUOUS,
                semantic_identity="inventory.entity.job_worker",
                original_value=semantic_value,
                target_type=target_type,
                resolver_provenance="JobWorkerSemanticResolver",
                candidates=[row[0] for row in rows]
            )
        else:
            return EntityResolutionResult(
                status=ResolutionStatus.RESOLVED,
                semantic_identity="inventory.entity.job_worker",
                original_value=semantic_value,
                resolved_value=rows[0][0],
                resolved_type="UUID",
                target_type=target_type,
                resolver_provenance="JobWorkerSemanticResolver"
            )
