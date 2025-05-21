from typing import IO
import datetime
from src.document_processing.helpers.jisebi_document import JISEBIDocument
from src.document_processing.helpers.jisebi_evaluation import JISEBIEvaluation
from src.document_processing.helpers.jisebi_reporting import JISEBIReporting
from src.database import db
from src.storage import storage
from src.task import task
import re
import uuid

# Helper
def parse_author_name(author_string):
    # Check for numbered author format: "First Author 1) , Second Author 2) , Third Author 3)"
    if re.search(r'\d\)', author_string):
        first_author = author_string.split(',')[0]  # Take only the first author
        first_author = re.sub(r'\s*\d\)', '', first_author).strip()  # Remove numbering like "1)"

    else:
        first_author = author_string.strip()

    # Handle cases where names are not in the usual "First Last" format
    name_parts = first_author.split()

    if len(name_parts) > 1:
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
    else:
        first_name = name_parts[0]
        last_name = ""
    
    return {"first_name": first_name, "last_name": last_name}

class JISEBIUploadService:

    async def upload_document(self, user_id:str, bytes:IO[bytes], json:bool=False):

        task_id = str(uuid.uuid4())
        cleanup_needed = False

        try:

            if (json == True):
                document = JISEBIDocument(bytes)
                evaluation = JISEBIEvaluation(document)
                report = JISEBIReporting(evaluation)
                await report.set_report()
                return report.jisebi_report

            # Process the document using the service
            document = JISEBIDocument(bytes)

            # Upload the processed document
            uploaded_blob = storage.upload(bytes, task_id, "input.docx")
            cleanup_needed = True

            if document.title["index"] != -1:
                title = document.title["content"]
            else:
                title = "Title Not Found"
            
            if document.authors["index"] != -1:
                authors = document.authors["authors"]["content"]
            else:
                authors = "Title Not Found"

            entry = {
                "user_id": user_id,
                "task_id": task_id,
                "title": title,
                "authors": authors,
                "status": "initializing",
            }

            doc_ref = db.add_document(data=entry, document_id=task_id)

            task.enqueue_task(task_id)

            # Add Queue
            db.update_document(document_id=doc_ref, data={
                'status': 'awaiting',
            })

            entry["status"] = 'awaiting'

            author_name = parse_author_name(authors)

            entry["authors"] = {
                "text": authors,
                "first_author": author_name
            }

            blob = storage.bucket.blob(f'{task_id}/input.docx')

            url = blob.generate_signed_url(
                expiration=datetime.timedelta(minutes=15),
                method="GET"
            )

            entry["url"] = url
            entry.pop("created_at", None)
            entry.pop("updated_at", None)
            return entry

        except Exception as e:
            if cleanup_needed:
                try:
                    if uploaded_blob:
                        storage.delete(uploaded_blob)
                    db.delete_document(task_id)
                except Exception as cleanup_error:
                    # Log cleanup error
                    print(f"Cleanup error: {cleanup_error}")
            
            raise Exception({
                'error': 'Failed to process document',
                'details': str(e)
            }) 

        # await report.generate_report()
        # return evaluation.generate_overall_summary()

    async def update_queue(self, user_id:str, task_id:str):

            try:

                document = db.get_document(task_id)
        
                # Check if document exists
                if document == None:
                    return {
                        "status": False,
                        "message":"Item not found or unauthorized access"
                    }

                # Validate user access
                if document.get("user_id") != user_id:
                    return {
                        "status": False,
                        "message": "Item not found or unauthorized access"
                    }

                
                if document.get("status") != "awaiting":
                    return {
                        "status": False,
                        "message":"Item is not awaiting"
                    }

                task.enqueue_task(task_id)

                # Add Queue
                db.update_document(document_id=task_id, data={
                    'status': 'queued',
                })

                return {
                    "status": True
                }

            except Exception as e:
                raise Exception({
                    'error': 'Failed to enqueu document',
                    'details': str(e)
                }) 

            # await report.generate_report()
            # return evaluation.generate_overall_summary()

    async def delete_document(self, user_id:str, task_id:str):

            try:

                document = db.get_document(task_id)
        
                # Check if document exists
                if document == None:
                    return {
                        "status": False,
                        "message":"Item not found or unauthorized access"
                    }

                # Validate user access
                if document.get("user_id") != user_id:
                    return {
                        "status": False,
                        "message": "Item not found or unauthorized access"
                    }

                
                if document.get("status") != "awaiting":
                    return {
                        "status": False,
                        "message":"Item is not awaiting"
                    }

                storage.delete(task_id)

                db.delete_document(document_id=task_id)

                return {
                    "status": True
                }

            except Exception as e:
                raise Exception({
                    'error': 'Failed to delete document',
                    'details': str(e)
                }) 

            # await report.generate_report()
            # return evaluation.generate_overall_summary()
