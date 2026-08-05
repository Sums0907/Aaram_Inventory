from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from uuid import UUID
from dependency_injector.wiring import Provide, inject
import hashlib
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.data_ingestion.schemas.import_job import ImportJobCreate, ImportJobResponse
from src.domains.data_ingestion.schemas.import_file import ImportFileCreate
from src.domains.data_ingestion.services.import_job import ImportJobService
from src.domains.data_ingestion.services.import_file import ImportFileService
from src.domains.data_ingestion.services.adapters.shopdeck_order import ShopDeckOrderAdapter
from src.domains.data_ingestion.services.adapters.shopdeck_tax import ShopDeckTaxAdapter
from src.domains.data_ingestion.services.adapters.shopdeck_cod_settlement import ShopDeckCODSettlementAdapter
from src.domains.data_ingestion.services.adapters.razorpay_settlement import RazorpaySettlementAdapter
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer

router = APIRouter(prefix="/shopdeck", tags=["Data Ingestion - ShopDeck"])

@router.post("/orders", response_model=SuccessResponse[ImportJobResponse])
@inject
async def upload_shopdeck_orders(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    # Assuming there's a predefined Integration UUID for ShopDeck. For now, we accept it as a query param or default it.
    integration_id: UUID = None, # In real life, we fetch this from DB
    current_user: CurrentUser = Depends(get_current_user),
    job_service: ImportJobService = Depends(Provide[DataIngestionContainer.import_job_service]),
    file_service: ImportFileService = Depends(Provide[DataIngestionContainer.import_file_service]),
    adapter: ShopDeckOrderAdapter = Depends(Provide[DataIngestionContainer.shopdeck_order_adapter])
):
    from uuid import uuid4
    user_uuid = UUID(current_user.id)
    
    # 1. Read file into memory
    content = await file.read()
    
    # 2. Compute MD5
    md5_hash = hashlib.md5(content).hexdigest()
    
    # 3. Create Import Job
    if not integration_id:
        integration_id = uuid4() # Dummy for now if not provided, since we don't have a real DB entry yet
        
    job_schema = ImportJobCreate(
        integration_id=integration_id,
        job_type="SHOPDECK_ORDERS",
        status="PROCESSING"
    )
    job = await job_service.create_job(job_schema, user_uuid)
    
    # 4. Create Import File record
    file_schema = ImportFileCreate(
        import_job_id=job.id,
        file_name=file.filename or "unknown.csv",
        file_size_bytes=len(content),
        mime_type=file.content_type or "text/csv",
        md5_hash=md5_hash
    )
    await file_service.create_file_record(file_schema, user_uuid)
    
    # 5. Process File via Adapter (Doing synchronously for now as requested by user in Phase 5 pivot)
    # "For Version 1, implement imports synchronously within the API request."
    try:
        await adapter.parse_and_ingest(content, job.id, user_uuid)
        await job_service.update_job_status(job.id, "COMPLETED", user_uuid)
    except Exception as e:
        await job_service.update_job_status(job.id, "FAILED", user_uuid)
        from src.foundation.exceptions.base import BadRequestException
        raise BadRequestException(message=f"Failed to process file. Ensure it is a valid CSV. Detail: {str(e)}")
    
    return SuccessResponse(data=ImportJobResponse.model_validate(job, from_attributes=True))

@router.post("/tax-invoices", response_model=SuccessResponse[ImportJobResponse])
@inject
async def upload_shopdeck_tax_invoices(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    integration_id: UUID = None,
    current_user: CurrentUser = Depends(get_current_user),
    job_service: ImportJobService = Depends(Provide[DataIngestionContainer.import_job_service]),
    file_service: ImportFileService = Depends(Provide[DataIngestionContainer.import_file_service]),
    adapter: ShopDeckTaxAdapter = Depends(Provide[DataIngestionContainer.shopdeck_tax_adapter])
):
    from uuid import uuid4
    user_uuid = UUID(current_user.id)
    content = await file.read()
    md5_hash = hashlib.md5(content).hexdigest()
    if not integration_id:
        integration_id = uuid4()
        
    job = await job_service.create_job(ImportJobCreate(integration_id=integration_id, job_type="SHOPDECK_TAX", status="PROCESSING"), user_uuid)
    await file_service.create_file_record(ImportFileCreate(import_job_id=job.id, file_name=file.filename or "tax.csv", file_size_bytes=len(content), mime_type=file.content_type or "text/csv", md5_hash=md5_hash), user_uuid)
    
    try:
        await adapter.parse_and_ingest(content, job.id, user_uuid)
        await job_service.update_job_status(job.id, "COMPLETED", user_uuid)
    except Exception as e:
        await job_service.update_job_status(job.id, "FAILED", user_uuid)
        from src.foundation.exceptions.base import BadRequestException
        raise BadRequestException(message=f"Failed to process file. Ensure it is a valid CSV. Detail: {str(e)}")
    
    return SuccessResponse(data=ImportJobResponse.model_validate(job, from_attributes=True))

@router.post("/cod-settlements", response_model=SuccessResponse[ImportJobResponse])
@inject
async def upload_shopdeck_cod_settlements(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    integration_id: UUID = None,
    current_user: CurrentUser = Depends(get_current_user),
    job_service: ImportJobService = Depends(Provide[DataIngestionContainer.import_job_service]),
    file_service: ImportFileService = Depends(Provide[DataIngestionContainer.import_file_service]),
    adapter: ShopDeckCODSettlementAdapter = Depends(Provide[DataIngestionContainer.shopdeck_cod_settlement_adapter])
):
    from uuid import uuid4
    user_uuid = UUID(current_user.id)
    content = await file.read()
    md5_hash = hashlib.md5(content).hexdigest()
    if not integration_id:
        integration_id = uuid4()
        
    job = await job_service.create_job(ImportJobCreate(integration_id=integration_id, job_type="SHOPDECK_COD_SETTLEMENT", status="PROCESSING"), user_uuid)
    await file_service.create_file_record(ImportFileCreate(import_job_id=job.id, file_name=file.filename or "cod.csv", file_size_bytes=len(content), mime_type=file.content_type or "text/csv", md5_hash=md5_hash), user_uuid)
    
    try:
        await adapter.parse_and_ingest(content, job.id, user_uuid)
        await job_service.update_job_status(job.id, "COMPLETED", user_uuid)
    except Exception as e:
        await job_service.update_job_status(job.id, "FAILED", user_uuid)
        from src.foundation.exceptions.base import BadRequestException
        raise BadRequestException(message=f"Failed to process file. Ensure it is a valid CSV. Detail: {str(e)}")
    
    return SuccessResponse(data=ImportJobResponse.model_validate(job, from_attributes=True))

@router.post("/razorpay-settlements", response_model=SuccessResponse[ImportJobResponse])
@inject
async def upload_razorpay_settlements(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    integration_id: UUID = None,
    current_user: CurrentUser = Depends(get_current_user),
    job_service: ImportJobService = Depends(Provide[DataIngestionContainer.import_job_service]),
    file_service: ImportFileService = Depends(Provide[DataIngestionContainer.import_file_service]),
    adapter: RazorpaySettlementAdapter = Depends(Provide[DataIngestionContainer.razorpay_settlement_adapter])
):
    from uuid import uuid4
    user_uuid = UUID(current_user.id)
    content = await file.read()
    md5_hash = hashlib.md5(content).hexdigest()
    if not integration_id:
        integration_id = uuid4()
        
    job = await job_service.create_job(ImportJobCreate(integration_id=integration_id, job_type="RAZORPAY_SETTLEMENT", status="PROCESSING"), user_uuid)
    await file_service.create_file_record(ImportFileCreate(import_job_id=job.id, file_name=file.filename or "razorpay.csv", file_size_bytes=len(content), mime_type=file.content_type or "text/csv", md5_hash=md5_hash), user_uuid)
    
    try:
        await adapter.parse_and_ingest(content, job.id, user_uuid)
        await job_service.update_job_status(job.id, "COMPLETED", user_uuid)
    except Exception as e:
        await job_service.update_job_status(job.id, "FAILED", user_uuid)
        from src.foundation.exceptions.base import BadRequestException
        raise BadRequestException(message=f"Failed to process file. Ensure it is a valid CSV. Detail: {str(e)}")
    
    return SuccessResponse(data=ImportJobResponse.model_validate(job, from_attributes=True))
