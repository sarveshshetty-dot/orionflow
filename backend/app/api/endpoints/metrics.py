from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db_session
from app.models.workers import Worker
from app.schemas.workers import WorkerResponse
from app.models.task_logs import TaskLog, TaskStatus
from app.models.workflow_runs import WorkflowRun

router = APIRouter()

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db_session)):
    # Total tasks
    result = await db.execute(select(func.count(TaskLog.id)))
    total_tasks = result.scalar() or 0

    # Failed tasks
    result = await db.execute(select(func.count(TaskLog.id)).where(TaskLog.status == TaskStatus.FAILED))
    failed_tasks = result.scalar() or 0

    # Total runs
    result = await db.execute(select(func.count(WorkflowRun.id)))
    total_runs = result.scalar() or 0

    # Task success rate
    success_rate = 0.0
    if total_tasks > 0:
        success_rate = ((total_tasks - failed_tasks) / total_tasks) * 100

    return {
        "total_tasks_processed": total_tasks,
        "failed_tasks": failed_tasks,
        "total_workflow_runs": total_runs,
        "success_rate_percent": round(success_rate, 2)
    }

@router.get("/workers", response_model=List[WorkerResponse])
async def list_workers(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Worker).order_by(Worker.last_seen.desc()))
    return result.scalars().all()
