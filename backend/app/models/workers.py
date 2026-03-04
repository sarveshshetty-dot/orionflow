import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class WorkerStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    BUSY = "BUSY"

class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[str] = mapped_column(String(100), primary_key=True) # E.g., hostname or UUID
    hostname: Mapped[str] = mapped_column(String(255))
    status: Mapped[WorkerStatus] = mapped_column(String(20), default=WorkerStatus.ONLINE)
    last_seen: Mapped[datetime] = mapped_column()
