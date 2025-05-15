from google.cloud import tasks_v2
from src.core.config import get_settings
import json

settings = get_settings()
project = settings.GCP_PROJECT_ID
queue = settings.GCP_TASK_QUEUE
location = settings.GCP_TASK_LOCATION
url = settings.SELF_URL

class CloudTask:
    def __init__(self, project_id, queue_name, location, base_url, endpoint):
        self.client       = tasks_v2.CloudTasksClient()
        self.project      = project_id
        self.queue        = queue_name
        self.location     = location
        self.base_url     = base_url
        self.endpoint_url = f"{base_url}{endpoint}"
        self.parent       = self.client.queue_path(self.project, self.location, self.queue)

    def enqueue_task(self, task_id: str):
        payload = json.dumps({"task_id": task_id})

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": self.endpoint_url,
                "headers": {"Content-Type": "application/json"},
                "body": payload.encode(),
                "oidc_token": {
                    "service_account_email": settings.GCP_TASK_SERVICE_ACCOUNT,
                    "audience": self.base_url
                }
            }
        }

        response = self.client.create_task(request={"parent": self.parent, "task": task})

        return (f"Created task {response.name}")
    
task = CloudTask(project_id=project, queue_name=queue, location=location, base_url=url, endpoint="/internal/api/process-document")
