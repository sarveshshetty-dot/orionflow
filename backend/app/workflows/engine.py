import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflows import Workflow
from app.models.workflow_runs import WorkflowRun, RunStatus
from app.models.task_logs import TaskLog, TaskStatus
from app.queue.redis_queue import RedisQueue
from app.core.redis import get_redis_client
from app.core.config import settings
import json

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.queue = RedisQueue()
        self.redis = get_redis_client()

    async def start_workflow(self, workflow_id: int) -> WorkflowRun:
        """Starts a new run for a given workflow."""
        workflow = await self.db.get(Workflow, workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")
        
        if not workflow.steps:
            raise ValueError("Workflow has no steps")

        run = WorkflowRun(
            workflow_id=workflow_id,
            status=RunStatus.RUNNING,
            current_step_index=0
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)

        # Enqueue the first step
        await self._enqueue_step(run, workflow)
        
        return run

    async def _enqueue_step(self, run: WorkflowRun, workflow: Workflow):
        """Enqueues the next task for a workflow run."""
        if run.current_step_index >= len(workflow.steps):
            # Workflow complete
            run.status = RunStatus.SUCCESS
            run.finished_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"WorkflowRun {run.id} finished successfully.")
            await self._broadcast_status(run)
            return

        step = workflow.steps[run.current_step_index]
        task_name = step.get("task_name")
        params = step.get("params", {})

        # Create TaskLog
        task_log = TaskLog(
            workflow_run_id=run.id,
            task_name=task_name,
            status=TaskStatus.PENDING,
            params=params
        )
        self.db.add(task_log)
        await self.db.commit()
        await self.db.refresh(task_log)

        # Push to Redis
        await self.queue.push_task(task_log.id)
        logger.info(f"Enqueued task {task_log.id} ({task_name}) for workflow run {run.id}")
        await self._broadcast_status(run)

    async def handle_task_completion(self, task_log_id: int):
        """Called by a worker after a task succeeds."""
        task_log = await self.db.get(TaskLog, task_log_id)
        if not task_log:
            logger.error(f"TaskLog {task_log_id} not found.")
            return

        run = await self.db.get(WorkflowRun, task_log.workflow_run_id)
        workflow = await self.db.get(Workflow, run.workflow_id)

        # Move to next step
        run.current_step_index += 1
        await self.db.commit()

        # Enqueue next task
        await self._enqueue_step(run, workflow)

    async def handle_task_failure(self, task_log_id: int):
        """Called by a worker after a task fails."""
        task_log = await self.db.get(TaskLog, task_log_id)
        if not task_log:
            return

        run = await self.db.get(WorkflowRun, task_log.workflow_run_id)

        if task_log.retries >= task_log.max_retries:
            # Mark workflow as completely failed
            run.status = RunStatus.FAILED
            run.finished_at = datetime.utcnow()
            task_log.status = TaskStatus.FAILED
            task_log.finished_at = datetime.utcnow()
            await self.db.commit()
            logger.error(f"WorkflowRun {run.id} failed at task {task_log.id}")
            await self._broadcast_status(run)
        else:
            # We retry
            task_log.retries += 1
            task_log.status = TaskStatus.RETRYING
            await self.db.commit()
            logger.warning(f"Retrying task {task_log.id} (Attempt {task_log.retries})")
            # Push back to queue
            await self.queue.push_task(task_log.id)

    async def _broadcast_status(self, run: WorkflowRun):
        """Broadcast workflow status over Redis pub/sub for WebSocket clients."""
        channel_name = f"{settings.LOGS_CHANNEL_PREFIX}:runs"
        message = {
            "type": "run_update",
            "run_id": run.id,
            "status": run.status.value if hasattr(run.status, "value") else run.status,
            "step_index": run.current_step_index
        }
        await self.redis.publish(channel_name, json.dumps(message))

    async def broadcast_log(self, task_log_id: int, message: str, level: str = "INFO"):
        """Broadcast real-time logs for a task."""
        channel_name = f"{settings.LOGS_CHANNEL_PREFIX}:tasks"
        log_payload = {
            "type": "log",
            "task_log_id": task_log_id,
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        }
        await self.redis.publish(channel_name, json.dumps(log_payload))

