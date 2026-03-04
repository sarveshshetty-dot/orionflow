from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ScheduleCreate(BaseModel):
    workflow_id: int
    cron_expression: str
    is_active: bool = True

class ScheduleResponse(ScheduleCreate):
    id: int
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
