import asyncio
import logging
from datetime import datetime
from croniter import croniter

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.schedules import Schedule
from app.workflows.engine import WorkflowEngine

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("Starting scheduler service...")
        
        while self.is_running:
            await self.check_schedules()
            # Sleep for a bit before checking again (e.g. 15 seconds)
            await asyncio.sleep(15)

    async def check_schedules(self):
        now = datetime.utcnow()
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Schedule).where(Schedule.is_active == True)
            )
            schedules = result.scalars().all()
            
            for schedule in schedules:
                if not schedule.next_run_at:
                    # Initialize next_run_at if never run
                    schedule.next_run_at = self.calculate_next_run(schedule.cron_expression, now)
                    await db.commit()
                
                if schedule.next_run_at and now >= schedule.next_run_at:
                    logger.info(f"Triggering scheduled workflow {schedule.workflow_id} (Schedule ID: {schedule.id})")
                    # Start workflow
                    engine = WorkflowEngine(db=db)
                    try:
                        await engine.start_workflow(schedule.workflow_id)
                    except Exception as e:
                        logger.error(f"Failed to start scheduled workflow! {e}")
                    
                    # Update next run
                    schedule.next_run_at = self.calculate_next_run(schedule.cron_expression, now)
                    await db.commit()

    def calculate_next_run(self, cron_expr: str, based_on: datetime) -> datetime:
        try:
            it = croniter(cron_expr, based_on)
            return it.get_next(datetime)
        except Exception as e:
            logger.error(f"Invalid cron expression '{cron_expr}': {e}")
            # If invalid, return a far future date to effectively pause it, but log error
            from datetime import timedelta
            return based_on + timedelta(days=365)

async def run_scheduler():
    service = SchedulerService()
    await service.start()

if __name__ == "__main__":
    asyncio.run(run_scheduler())
