from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db_session
from app.models.task_logs import TaskLog
from app.schemas.tasks import TaskLogResponse

router = APIRouter()

@router.get("/run/{run_id}", response_model=List[TaskLogResponse])
async def get_task_logs_for_run(run_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(TaskLog).where(TaskLog.workflow_run_id == run_id).order_by(TaskLog.id.asc())
    )
    return result.scalars().all()

@router.get("/", response_model=List[TaskLogResponse])
async def list_tasks(limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(TaskLog).order_by(TaskLog.id.desc()).limit(limit)
    )
    return result.scalars().all()
