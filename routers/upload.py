from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.jisebi_processing_service import JISEBIProcessingService
import io

router = APIRouter()

@router.post("/upload")
async def complex_operation_endpoint(file: UploadFile = File(...), service: JISEBIProcessingService = Depends()):
    # Validate file type
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Only DOCX files are supported."
        )
    
    contents = await file.read()
    bytes_io = io.BytesIO(contents)
    
    try:
        reporting = await service.process_document(bytes_io)
        # report = await reporting.generate_report()

        return StreamingResponse(
            reporting,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reporting-result.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

