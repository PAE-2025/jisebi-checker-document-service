from typing import IO
import datetime
from src.document_processing.helpers.jisebi_document import JISEBIDocument
from src.document_processing.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_processing.helpers.jisebi_reporting import JISEBIReporting
from src.database import db
from src.storage import storage
import uuid

class JISEBIProcessingService:

    async def process_document(self, task_id) -> JISEBIReporting:

        query = db.collection.where("task_id", "==", task_id).where("status", "==", "queued").limit(1).stream()
        
        task_doc = next(query, None)



        if task_doc:
            # Process Task
            return "success"

        raise Exception("Cannot find task (incorrect id or already processed)")