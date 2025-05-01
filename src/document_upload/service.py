from typing import IO
from src.document_upload.helpers.jisebi_document import JISEBIDocument
from src.document_upload.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_upload.helpers.jisebi_reporting import JISEBIReporting

class JISEBIProcessingService:
    
    async def process_document(self, bytes:IO[bytes], json:bool=False) -> JISEBIReporting:
        # Process the document using the service
        document = JISEBIDocument(bytes)
        evaluation = JISEBIEvaluation(document)
        report = JISEBIReporting(evaluation)
        if (json == True):
            await report.set_report()
            return report.jisebi_report
        else:
            return await report.generate_final_report()
        # await report.generate_report()
        # return evaluation.generate_overall_summary()