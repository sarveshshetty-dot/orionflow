from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models.workflow_runs import RunStatus

class WorkflowStep(BaseModel):
    task_name: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowResponse(WorkflowBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkflowRunWithLogs(BaseModel):
    id: int
    workflow_id: int
    status: RunStatus
    current_step_index: int
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
