import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"))
    status: Mapped[RunStatus] = mapped_column(String(20), default=RunStatus.PENDING)
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    
    finished_at: Mapped[Optional[datetime]] = mapped_column()
    
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="runs")
    task_logs: Mapped[List["TaskLog"]] = relationship("TaskLog", back_populates="workflow_run", cascade="all, delete-orphan")
