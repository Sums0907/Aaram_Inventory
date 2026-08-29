import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.capabilities.r7_protocol import IR7Capability
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity
from src.domains.inventory.services.goods_receipt import GoodsReceiptService
from src.domains.inventory.services.purchase_return import PurchaseReturnService
from src.domains.inventory.services.transformation_engine import InventoryTransformationEngine
from src.domains.inventory.services.job_work import JobWorkService
from src.domains.inventory.services.exception import InventoryExceptionService
from src.domains.inventory.services.movement import InventoryMovementService
from src.foundation.exceptions.base import ValidationException, NotFoundException, AlreadyExistsException
from pydantic import ValidationError

def _get_entity_id(resolved_candidates: Dict[str, List[CandidateEntity]], entity_urn: str) -> uuid.UUID | None:
    candidates = resolved_candidates.get(entity_urn, [])
    if candidates and len(candidates) == 1:
        return uuid.UUID(candidates[0].business_id)
    return None

def _get_param_value(understanding: ConversationalUnderstanding, identity: str) -> Any | None:
    for p in understanding.parameters:
        if p.identity == identity:
            return p.value
    return None

class R7GoodsReceiptCapability(IR7Capability):
    def __init__(self, goods_receipt_service: GoodsReceiptService):
        self.goods_receipt_service = goods_receipt_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:goods_receipt"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.supplier", "inventory.entity.sku", "inventory.entity.warehouse"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        has_supplier = any(c.identity == "inventory.entity.supplier" for c in understanding.entities)
        has_action = any(c.identity == "inventory.action.receive" for c in understanding.entities)
        return has_supplier and has_action

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            supplier_id = _get_entity_id(resolved_candidates, "inventory.entity.supplier")
            sku_id = _get_entity_id(resolved_candidates, "inventory.entity.sku")
            warehouse_id = _get_entity_id(resolved_candidates, "inventory.entity.warehouse")
            
            if not supplier_id or not sku_id or not warehouse_id:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing unique resolved entities for supplier, sku, or warehouse"}

            quantity = _get_param_value(understanding, "inventory.numeric.quantity")
            if quantity is None or float(quantity) <= 0:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing or invalid quantity parameter"}

            from src.domains.inventory.schemas.goods_receipt import GoodsReceiptCreate, GoodsReceiptItemCreate
            from src.domains.inventory.schemas.enums import GoodsReceiptType
            from datetime import date
            
            schema = GoodsReceiptCreate(
                grn_number=None,
                supplier_id=supplier_id,
                warehouse_id=warehouse_id,
                receipt_date=date.today(),
                receipt_type=GoodsReceiptType.RAW_MATERIAL_RECEIPT,
                items=[GoodsReceiptItemCreate(sku_id=sku_id, quantity=float(quantity))]
            )
            
            created_by = execution_context.get("user_id", uuid.uuid4())
            
            doc = await self.goods_receipt_service.create(schema, created_by)
            
            return {
                "status": "SUCCESS",
                "document_id": str(doc.id),
                "document_number": doc.grn_number,
                "message": f"Successfully created Goods Receipt {doc.grn_number}"
            }
        except (ValidationException, NotFoundException, AlreadyExistsException, ValidationError) as e:
            return {"status": "EXECUTION_LIMITATION", "reason": f"Domain validation failed: {str(e)}"}


class R7PurchaseReturnCapability(IR7Capability):
    def __init__(self, purchase_return_service: PurchaseReturnService):
        self.purchase_return_service = purchase_return_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:purchase_return"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.supplier", "inventory.entity.sku", "inventory.entity.warehouse"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        has_action = any(c.identity == "inventory.action.return" for c in understanding.entities)
        return has_action

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            supplier_id = _get_entity_id(resolved_candidates, "inventory.entity.supplier")
            sku_id = _get_entity_id(resolved_candidates, "inventory.entity.sku")
            warehouse_id = _get_entity_id(resolved_candidates, "inventory.entity.warehouse")
            
            if not supplier_id or not sku_id or not warehouse_id:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing unique resolved entities for supplier, sku, or warehouse"}

            quantity = _get_param_value(understanding, "inventory.numeric.quantity")
            if quantity is None or float(quantity) <= 0:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing or invalid quantity parameter"}

            from src.domains.inventory.schemas.purchase_return import PurchaseReturnCreate, PurchaseReturnItemCreate
            from datetime import date
            
            schema = PurchaseReturnCreate(
                return_number=None,
                supplier_id=supplier_id,
                warehouse_id=warehouse_id,
                return_date=date.today(),
                items=[PurchaseReturnItemCreate(sku_id=sku_id, quantity=float(quantity))]
            )
            
            created_by = execution_context.get("user_id", uuid.uuid4())
            
            doc = await self.purchase_return_service.create(schema, created_by)
            
            return {
                "status": "SUCCESS",
                "document_id": str(doc.id),
                "document_number": doc.return_number,
                "message": f"Successfully created Purchase Return {doc.return_number}"
            }
        except (ValidationException, NotFoundException, AlreadyExistsException, ValidationError) as e:
            return {"status": "EXECUTION_LIMITATION", "reason": f"Domain validation failed: {str(e)}"}


class R7TransformationCapability(IR7Capability):
    def __init__(self, transformation_engine: InventoryTransformationEngine):
        self.transformation_engine = transformation_engine

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:transformation"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        return any(c.identity == "inventory.action.transform" for c in understanding.entities)

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "EXECUTION_LIMITATION", "reason": "Requires TransformationRequest schema and reference_document"}


class R7JobWorkIssueCapability(IR7Capability):
    def __init__(self, job_work_service: JobWorkService):
        self.job_work_service = job_work_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:jobwork_issue"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku", "inventory.entity.job_worker"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        return any(c.identity == "inventory.action.issue_jobwork" for c in understanding.entities)

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            job_worker_id = _get_entity_id(resolved_candidates, "inventory.entity.job_worker")
            sku_id = _get_entity_id(resolved_candidates, "inventory.entity.sku")
            
            if not job_worker_id or not sku_id:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing unique resolved entities for job worker or sku"}

            quantity = _get_param_value(understanding, "inventory.numeric.quantity")
            if quantity is None or float(quantity) <= 0:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing or invalid quantity parameter"}

            from src.domains.inventory.schemas.job_work import JobWorkIssueCreate
            
            schema = JobWorkIssueCreate(
                job_worker_id=job_worker_id,
                item_id=sku_id,
                quantity=float(quantity)
            )
            
            created_by = execution_context.get("user_id", uuid.uuid4())
            
            doc = await self.job_work_service.issue_material(schema, created_by)
            
            return {
                "status": "SUCCESS",
                "document_id": str(doc.id),
                "document_number": doc.issue_reference,
                "message": f"Successfully issued Job Work material {doc.issue_reference}"
            }
        except (ValidationException, NotFoundException, AlreadyExistsException, ValidationError) as e:
            return {"status": "EXECUTION_LIMITATION", "reason": f"Domain validation failed: {str(e)}"}


class R7JobWorkReturnCapability(IR7Capability):
    def __init__(self, job_work_service: JobWorkService):
        self.job_work_service = job_work_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:jobwork_return"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku", "inventory.entity.job_worker"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        return any(c.identity == "inventory.action.return_jobwork" for c in understanding.entities)

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            job_worker_id = _get_entity_id(resolved_candidates, "inventory.entity.job_worker")
            sku_id = _get_entity_id(resolved_candidates, "inventory.entity.sku")
            
            if not job_worker_id or not sku_id:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing unique resolved entities for job worker or sku"}

            quantity = _get_param_value(understanding, "inventory.numeric.quantity")
            if quantity is None or float(quantity) <= 0:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing or invalid quantity parameter"}

            from src.domains.inventory.schemas.job_work import JobWorkReturnCreate
            
            schema = JobWorkReturnCreate(
                job_worker_id=job_worker_id,
                item_id=sku_id,
                quantity=float(quantity)
            )
            
            created_by = execution_context.get("user_id", uuid.uuid4())
            
            doc = await self.job_work_service.return_material(schema, created_by)
            
            return {
                "status": "SUCCESS",
                "document_id": str(doc.id),
                "document_number": doc.return_number,
                "message": f"Successfully returned Job Work material {doc.return_number}"
            }
        except (ValidationException, NotFoundException, AlreadyExistsException, ValidationError) as e:
            return {"status": "EXECUTION_LIMITATION", "reason": f"Domain validation failed: {str(e)}"}


class R7ExceptionResolutionCapability(IR7Capability):
    def __init__(self, exception_service: InventoryExceptionService):
        self.exception_service = exception_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:exception_resolution"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.exception"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        return any(c.identity == "inventory.action.resolve_exception" for c in understanding.entities)

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            exception_id = _get_entity_id(resolved_candidates, "inventory.entity.exception")
            
            if not exception_id:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing unique resolved entity for exception"}

            resolution_notes = _get_param_value(understanding, "inventory.text.resolution_notes")
            if not resolution_notes:
                return {"status": "EXECUTION_LIMITATION", "reason": "Missing required resolution_notes parameter"}

            await self.exception_service.resolve_exception(exception_id, str(resolution_notes))
            
            return {
                "status": "SUCCESS",
                "message": f"Successfully resolved exception"
            }
        except (ValidationException, NotFoundException, AlreadyExistsException, ValidationError) as e:
            return {"status": "EXECUTION_LIMITATION", "reason": f"Domain validation failed: {str(e)}"}


class R7StockAdjustmentCapability(IR7Capability):
    def __init__(self, movement_service: InventoryMovementService):
        self.movement_service = movement_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:stock_adjustment"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku", "inventory.entity.warehouse"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
        return any(c.identity == "inventory.action.adjust_stock" for c in understanding.entities)

    async def execute(self, understanding: ConversationalUnderstanding, resolved_candidates: Dict[str, List[CandidateEntity]], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "EXECUTION_LIMITATION", "reason": "Stock adjustment requires careful validation of reference fields (reference_type, reference_number, reference_id) which are not cleanly modeled in the current parameters"}
