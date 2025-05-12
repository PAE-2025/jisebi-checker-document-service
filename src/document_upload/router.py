
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from src.document_upload.service import JISEBIUploadService
from src.document_upload.dependencies import get_upload_service
from typing import Optional
from src.database import db
from src.storage import storage
import io
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def complex_operation_endpoint(
    request: Request, 
    file: UploadFile = File(...), 
    service: JISEBIUploadService = Depends(get_upload_service)
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
            reporting = await service.upload_document(user['id'], bytes_io, True)
            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "data": reporting
                }
            )
            
        else:
            reporting = await service.upload_document(user['id'], bytes_io)
            reporting["success"] = True
            return JSONResponse(
                content=reporting,
                status_code=200
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get(
    "/upload", 
    # response_model=List[Upload],
    summary="List Uploads",
    description="List Uploads with optional filtering by status."
)
async def list_uploads(
    request: Request,
    status: Optional[str] = Query(None, description="Filter Uploads by status"),
    skip: int = Query(0, ge=0, description="Number of Uploads to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of Uploads to return")
):
    """List Uploads with pagination and optional status filtering."""
    uid = request.state.user["id"]

    query = {
        "user_id": uid
    }

    if status:
        query["status"] = status

    try: 
    
        uploads = db.list_documents(
            query=query,
            sort_by="created_at",
            sort_direction="DESCENDING",  # Descending, newest first
            limit=limit
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching history")
  
    return uploads

@router.get(
    "/download/{task_id}", 
    # response_model=List[Upload],
    summary="List Uploads",
    description="List Uploads with optional filtering by status."
)
async def download(
    request: Request,
    task_id: str,
):
    
    """List Uploads with pagination and optional status filtering."""
    uid = request.state.user["id"]

    document = db.get_document(task_id)
    
    # Check if document exists
    if document == None:
        raise HTTPException(status_code=400, detail="Item not found or unauthorized access")

    # Validate user access
    if document.get("user_id") != uid:
        raise HTTPException(status_code=400, detail="Item not found or unauthorized access")
    

    if document.get("status") != "processed":
        raise HTTPException(status_code=400, detail="Item is not finished processing")
    
    try:
    
        reporting = storage.download(f"{task_id}/output.pdf")
        reporting.seek(0)

        return StreamingResponse(
            reporting,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reporting-result.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Download failed")

