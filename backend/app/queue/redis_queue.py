import json
from typing import Any, Dict, Optional
import redis.asyncio as redis

from app.core.config import settings
from app.core.redis import get_redis_client

class RedisQueue:
    def __init__(self, queue_name: str = settings.TASK_QUEUE_NAME):
        self.queue_name = queue_name
        self.redis: redis.Redis = get_redis_client()

    async def push_task(self, task_log_id: int):
        """Push a task log ID to the queue for a worker to pick up."""
        await self.redis.lpush(self.queue_name, str(task_log_id))

    async def pop_task(self, timeout: int = 5) -> Optional[int]:
        """Blocking pop a task from the queue."""
        result = await self.redis.brpop([self.queue_name], timeout=timeout)
        if result:
            queue, data = result
            return int(data)
        return None

    async def get_queue_size(self) -> int:
        return await self.redis.llen(self.queue_name)

queue = RedisQueue()
