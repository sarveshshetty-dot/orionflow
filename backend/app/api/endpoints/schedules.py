from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db_session
from app.models.schedules import Schedule
from app.schemas.schedules import ScheduleCreate, ScheduleResponse

router = APIRouter()

@router.post("/", response_model=ScheduleResponse)
async def create_schedule(schedule_in: ScheduleCreate, db: AsyncSession = Depends(get_db_session)):
    schedule = Schedule(
        workflow_id=schedule_in.workflow_id,
        cron_expression=schedule_in.cron_expression,
        is_active=schedule_in.is_active
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.get("/", response_model=List[ScheduleResponse])
async def list_schedules(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Schedule).order_by(Schedule.id.desc()))
    return result.scalars().all()
