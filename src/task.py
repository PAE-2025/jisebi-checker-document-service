from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import json

client = tasks_v2.CloudTasksClient()
project = "x-sorter-458402-e1"
queue = "jisebi-document-processing"
location = "asia-southeast2"
url = "placeholder"
parent = client.queue_path(project, location, queue)

class CloudTask:
    def __init__(self, project_id, queue_name, location, endpoint):
        self.client   = tasks_v2.CloudTasksClient()
        self.project  = project_id
        self.queue    = queue_name
        self.location = location
        self.url      = endpoint

    def enqueue_task(self, doc_id: str):
        payload = json.dumps({"doc_id": doc_id})

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": self.url,
                "headers": {"Content-Type": "application/json"},
                "body": payload.encode(),
            }
        }

        response = client.create_task(request={"parent": parent, "task": task})
        return (f"Created task {response.name}")
