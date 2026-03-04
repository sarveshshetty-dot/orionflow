import asyncio
import logging
import socket
from datetime import datetime
import traceback

from app.core.database import AsyncSessionLocal
from app.queue.redis_queue import RedisQueue
from app.tasks.registry import registry
from app.workflows.engine import WorkflowEngine
from app.models.task_logs import TaskLog, TaskStatus
from app.models.workers import Worker, WorkerStatus

logger = logging.getLogger(__name__)

class WorkerNode:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.queue = RedisQueue()
        self.is_running = False

    async def register_worker(self, db):
        worker = await db.get(Worker, self.hostname)
        if not worker:
            worker = Worker(id=self.hostname, hostname=self.hostname, status=WorkerStatus.ONLINE, last_seen=datetime.utcnow())
            db.add(worker)
        else:
            worker.status = WorkerStatus.ONLINE
            worker.last_seen = datetime.utcnow()
        await db.commit()

    async def unregister_worker(self, db):
        worker = await db.get(Worker, self.hostname)
        if worker:
            worker.status = WorkerStatus.OFFLINE
            worker.last_seen = datetime.utcnow()
            await db.commit()

    async def heartbeat(self):
        """Periodically update last_seen timestamp."""
        while self.is_running:
            try:
                async with AsyncSessionLocal() as db:
                    worker = await db.get(Worker, self.hostname)
                    if worker:
                        worker.last_seen = datetime.utcnow()
                        await db.commit()
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            await asyncio.sleep(60)

    async def start(self):
        self.is_running = True
        logger.info(f"Starting worker node on {self.hostname}...")
        
        async with AsyncSessionLocal() as db:
            await self.register_worker(db)
            
        asyncio.create_task(self.heartbeat())

        try:
            while self.is_running:
                task_log_id = await self.queue.pop_task(timeout=5)
                if task_log_id:
                    asyncio.create_task(self.process_task(task_log_id))
        except asyncio.CancelledError:
            pass
        finally:
            self.is_running = False
            async with AsyncSessionLocal() as db:
                await self.unregister_worker(db)

    async def process_task(self, task_log_id: int):
        logger.info(f"Processing task {task_log_id}")
        async with AsyncSessionLocal() as db:
            engine = WorkflowEngine(db=db)
            
            # Fetch task
            task_log = await db.get(TaskLog, task_log_id)
            if not task_log:
                logger.error(f"TaskLog {task_log_id} not found. Dropping.")
                return

            # Mark as running
            task_log.status = TaskStatus.RUNNING
            task_log.started_at = datetime.utcnow()
            task_log.worker_id = self.hostname
            await db.commit()
            
            await engine.broadcast_log(task_log_id, f"Worker {self.hostname} starting task.")

            try:
                # Get function
                func = registry.get_task(task_log.task_name)
                
                # Execute
                result = await func(task_log.params or {})
                
                # Mark Success
                task_log.status = TaskStatus.SUCCESS
                task_log.result = result
                task_log.finished_at = datetime.utcnow()
                await db.commit()
                logger.info(f"Task {task_log_id} completed successfully.")
                await engine.broadcast_log(task_log_id, f"Task completed successfully: {result}")
                
                # Advance workflow
                await engine.handle_task_completion(task_log_id)

            except Exception as e:
                # Attempt to catch and format traceback
                error_msg = str(e)
                tb = traceback.format_exc()
                
                # Mark failed for now (engine will handle retry logic)
                task_log.error_message = f"{error_msg}\n{tb}"
                await db.commit()
                logger.error(f"Task {task_log_id} failed: {error_msg}")
                await engine.broadcast_log(task_log_id, f"Task failed: {error_msg}", level="ERROR")
                
                await engine.handle_task_failure(task_log_id)

async def run_worker():
    node = WorkerNode()
    await node.start()

if __name__ == "__main__":
    import app.tasks.definitions # ensure tasks are loaded
    asyncio.run(run_worker())
