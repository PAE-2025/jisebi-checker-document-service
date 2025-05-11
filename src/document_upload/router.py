
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from src.document_upload.service import JISEBIProcessingService
from src.document_upload.dependencies import get_processing_service
from typing import Optional
from src.database import db
import io
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def complex_operation_endpoint(
    request: Request, 
    file: UploadFile = File(...), 
    service: JISEBIProcessingService = Depends(get_processing_service)
    ):

    # Validate file type
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Only DOCX files are supported."
        )
    
    contents = await file.read()
    bytes_io = io.BytesIO(contents)

    
    try:
        
        accept_header = request.headers.get("accept")

        user = request.state.user

        # Return a specific response based on the 'Accept' header
        if "application/json" in accept_header:
            reporting = await service.process_document(user['id'], bytes_io, True)
            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "data": reporting
                }
            )
            
        else:
            reporting = await service.process_document(user['id'], bytes_io)
            return StreamingResponse(
                reporting,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=reporting-result.pdf"}
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get(
    "/upload", 
    # response_model=List[Upload],
    summary="List Uploads",
    description="List Uploads with optional filtering by status."
)
async def list_Uploads(
    request: Request,
    status: Optional[str] = Query(None, description="Filter Uploads by status"),
    skip: int = Query(0, ge=0, description="Number of Uploads to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of Uploads to return")
):
    """List Uploads with pagination and optional status filtering."""
    query = {}
    if status:
        query["status"] = status
    
    uploads = await db.list_documents(
        "uploads",
        query=query,
        sort_by="created_at",
        sort_direction=-1,  # Descending, newest first
        skip=skip,
        limit=limit
    )
    
    # Convert _id to id for response
    for upload in uploads:
        upload["id"] = str(upload.pop("_id"))
  
    return uploads