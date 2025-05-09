from typing import IO
import datetime
from src.document_upload.helpers.jisebi_document import JISEBIDocument
from src.document_upload.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_upload.helpers.jisebi_reporting import JISEBIReporting
from src.database import upload_collections

class JISEBIProcessingService:
    
    async def process_document(self, user_id:str, bytes:IO[bytes], json:bool=False) -> JISEBIReporting:
        # Process the document using the service
        document = JISEBIDocument(bytes)

        await self.save_to_db(user_id, document.title["content"], document.authors["authors"]["content"], "null", "on_queue")

        evaluation = JISEBIEvaluation(document)
        report = JISEBIReporting(evaluation)
        if (json == True):
            await report.set_report()
            return report.jisebi_report
        else:
            return await report.generate_final_report()
        # await report.generate_report()
        # return evaluation.generate_overall_summary()

    async def save_to_db(self, user_id: str, title:str, authors:str, file_uri: str, status: str):
        entry = {
            "user_id": user_id,
            "title": title,
            "authors": authors,
            "file_uri": file_uri,
            "status": status,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        await upload_collections.insert_one(entry)
        return entry