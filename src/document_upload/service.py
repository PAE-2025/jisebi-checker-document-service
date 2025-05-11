from typing import IO
import datetime
from src.document_upload.helpers.jisebi_document import JISEBIDocument
from src.document_upload.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_upload.helpers.jisebi_reporting import JISEBIReporting
from src.database import db
import uuid

class JISEBIProcessingService:

    
    async def process_document(self, user_id:str, bytes:IO[bytes], json:bool=False) -> JISEBIReporting:

        task_id = str(uuid.uuid4())
        cleanup_needed = False

        try:
            # Process the document using the service
            document = JISEBIDocument(bytes)

            entry = {
                "user_id": user_id,
                "task_id": task_id,
                "title": document.title["content"],
                "authors": document.authors["authors"]["content"],
                "status": "initializing",
            }

            doc_ref = db.add_document(data=entry, document_id=task_id)

            #Add Queue

            db.update_document(document_id=doc_ref, data={
                'status': 'queued',
            })

            return {
                "task_id": task_id,
                "status": "queued",
            }

        except Exception as e:
            if cleanup_needed:
                try:
                    db.delete_document(task_id)
                except Exception as cleanup_error:
                    # Log cleanup error
                    print(f"Cleanup error: {cleanup_error}")
            
            raise Exception({
                'error': 'Failed to process document',
                'details': str(e)
            }) 

        evaluation = JISEBIEvaluation(document)
        report = JISEBIReporting(evaluation)
        if (json == True):
            await report.set_report()
            return report.jisebi_report
        else:
            return await report.generate_final_report()
        # await report.generate_report()
        # return evaluation.generate_overall_summary()
