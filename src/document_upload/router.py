from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from src.document_upload.service import JISEBIProcessingService
from src.document_upload.dependencies import get_processing_service
import io
import logging

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

