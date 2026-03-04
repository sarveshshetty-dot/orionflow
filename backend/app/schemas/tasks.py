from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.task_logs import TaskStatus

class TaskLogResponse(BaseModel):
    id: int
    workflow_run_id: int
    task_name: str
    status: TaskStatus
    params: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    retries: int
    worker_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)
