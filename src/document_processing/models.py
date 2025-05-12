from pydantic import BaseModel

class TaskProcessingRequest(BaseModel):
    task_id: str 