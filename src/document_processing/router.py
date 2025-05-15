
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from src.document_processing.service import JISEBIProcessingService
from src.document_processing.dependencies import get_processing_service
from src.document_processing.models import TaskProcessingRequest
import src.document_processing.docs as docs
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/process-document", **docs.document_processing)
async def processing_endpoint(
    request: Request, 
    task_data: TaskProcessingRequest,
    service: JISEBIProcessingService = Depends(get_processing_service)
    ):
    if not task_data.task_id:
        raise HTTPException(status_code=400, detail="Task ID is required")

    try:
        result = await service.process_document(task_data.task_id)
        return {"message": "Document processed successfully", "task_id": task_data.task_id, "result": result}
    except Exception as e:
        return JSONResponse(
            content= {
                "status": False,
                "message": str(e)
            },
            status_code=422
        )

    