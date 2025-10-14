
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from src.document_processing.service import JISEBIProcessingService
from src.document_processing.dependencies import get_processing_service
from src.document_processing.models import TaskProcessingRequest
import src.document_processing.docs as docs
import logging
import json
import traceback
from src.task import task

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_ATTEMPTS = 10  # Match your queue config

@router.post("/process-document", **docs.document_processing)
async def processing_endpoint(
    request: Request, 
    task_data: TaskProcessingRequest,
    service: JISEBIProcessingService = Depends(get_processing_service)
    ):

    retry_count = int(request.headers.get("x-cloudtasks-taskretrycount", "0"))

    if not task_data.task_id:
        raise HTTPException(status_code=400, detail="Task ID is required")

    try:
        result = await service.process_document(task_data.task_id)
        return {"message": "Document processed successfully", "task_id": task_data.task_id, "result": result}
    except Exception as e:
        if retry_count + 1 == MAX_ATTEMPTS:
            task.enqueue_task(task_data.task_id)

        return JSONResponse(
            content= {
                "status": False,
                "message": json.loads(json.dumps({
                    "error": str(e),
                    "type": type(e).__name__
                }))
            },
            status_code=422
        )
    
@router.post("/preview-result", **docs.document_processing)
async def processing_endpoint(
    request: Request, 
    task_data: TaskProcessingRequest,
    service: JISEBIProcessingService = Depends(get_processing_service)
    ):

    retry_count = int(request.headers.get("x-cloudtasks-taskretrycount", "0"))

    if not task_data.task_id:
        raise HTTPException(status_code=400, detail="Task ID is required")

    try:
        result, report = await service.preview_result(task_data.task_id)
        result.seek(0)
        accept_header = request.headers.get("accept", "")

        if "application/json" in accept_header:
            return JSONResponse(content=report)
        elif "format/json" in accept_header:
            return JSONResponse(content=report)
        else:
            return StreamingResponse(
                result,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={task_data.task_id}.pdf",
                }
            )
    except Exception as e:
        if retry_count + 1 == MAX_ATTEMPTS:
            task.enqueue_task(task_data.task_id)

        return JSONResponse(
            content= {
                "status": False,
                "message": json.loads(json.dumps({
                    "error": str(e),
                    "type": type(e).__name__
                }))
            },
            status_code=422
        )
    
    