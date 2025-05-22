from typing import IO
import datetime
from src.document_processing.helpers.jisebi_document import JISEBIDocument
from src.document_processing.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_processing.helpers.jisebi_reporting import JISEBIReporting
from src.database import db
from src.storage import storage
import uuid
import traceback

class JISEBIProcessingService:

    async def process_document(self, task_id) -> JISEBIReporting:

        query = db.collection.where("task_id", "==", task_id).where("status", "==", "queued").limit(1).stream()
        
        task_doc = next(query, None)



        if task_doc:

            try:

                file = storage.download(f"{task_id}/input.docx")
                file.seek(0)

                # Process Task
                document = JISEBIDocument(file)
                evaluation = JISEBIEvaluation(document)
                report = JISEBIReporting(evaluation)
                
                pdf_report = await report.generate_final_report()

                storage.upload(pdf_report, task_id, "output.pdf")

                db.update_document(document_id=task_id, data={
                    'status': 'processed',
                })

                storage.delete(f"{task_id}/input.docx")
            
                return "success"
            
            except Exception as e:
                traceback.print_exc()
                raise Exception(({
                    "failure": "Failed processing document",
                    "detail": e
            }))

        raise Exception("Cannot find task (incorrect id or already processed)")