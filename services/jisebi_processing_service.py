from typing import IO
from helpers.jisebi_document import JISEBIDocument
from helpers.jisebi_evaluation import JISEBIEvaluation
from helpers.jisebi_reporting import JISEBIReporting

class JISEBIProcessingService:
    
    async def process_document(self, bytes:IO[bytes]) -> JISEBIReporting:
        # Process the document using the service
        document = JISEBIDocument(bytes)
        evaluation = JISEBIEvaluation(document)
        report = JISEBIReporting(evaluation)
        # await report.save_dashboard_to_file()
        return await report.generate_final_report()
        # await report.generate_report()
        # return evaluation.generate_overall_summary()