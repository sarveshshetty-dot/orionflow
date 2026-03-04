"""
Startup script that creates all database tables using SQLAlchemy's create_all().
This is used in development/Docker to avoid needing alembic version files.
In production, use proper alembic migrations.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

# Import all models to ensure they are registered on the Base metadata
from app.models.base import Base
from app.models.users import User
from app.models.workflows import Workflow
from app.models.workflow_runs import WorkflowRun
from app.models.task_logs import TaskLog
from app.models.workers import Worker
from app.models.schedules import Schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Creating database tables if they don't exist...")
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    logger.info("Database tables ready.")

if __name__ == "__main__":
    asyncio.run(init_db())
