from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.workers import WorkerStatus

class WorkerResponse(BaseModel):
    id: str
    hostname: str
    status: WorkerStatus
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True)
