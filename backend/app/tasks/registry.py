import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable

logger = logging.getLogger(__name__)

# Type alias for our task functions. Must be async, take params as dict, and return a dict.
TaskFunction = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]

class TaskRegistry:
    def __init__(self):
        self._tasks: Dict[str, TaskFunction] = {}

    def register(self, name: str):
        """Decorator to register a task function."""
        def decorator(func: TaskFunction) -> TaskFunction:
            self._tasks[name] = func
            logger.info(f"Registered task: {name}")
            return func
        return decorator

    def get_task(self, name: str) -> TaskFunction:
        if name not in self._tasks:
            raise ValueError(f"Task '{name}' not found in registry.")
        return self._tasks[name]

    def list_tasks(self) -> list[str]:
        return list(self._tasks.keys())

registry = TaskRegistry()
