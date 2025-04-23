from typing import IO
from helpers.jisebi_document import JISEBIDocument
from helpers.jisebi_evaluation import JISEBIEvaluation
from helpers.jisebi_reporting import JISEBIReporting

class JISEBIProcessingService:
    
    def process_document(self, bytes:IO[bytes]) -> JISEBIReporting:
        # Process the document using the service
        document = JISEBIDocument(bytes)
        evaluation = JISEBIEvaluation(document)
        report = JISEBIReporting(evaluation)
        return report