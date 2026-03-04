import asyncio
from typing import Dict, Any
from app.tasks.registry import registry

@registry.register("http_request")
async def http_request_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """A generic task to make an HTTP request."""
    # Dummy implementation for now
    url = params.get("url")
    method = params.get("method", "GET")
    await asyncio.sleep(1) # simulate network latency
    return {"status_code": 200, "data": f"Fetched from {url} using {method}"}

@registry.register("data_transform")
async def data_transform_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """A task to transform data."""
    await asyncio.sleep(0.5)
    input_data = params.get("input", "")
    return {"result": str(input_data).upper()}

@registry.register("wait")
async def wait_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """A task to wait for n seconds."""
    seconds = params.get("seconds", 1)
    await asyncio.sleep(seconds)
    return {"message": f"Waited for {seconds} seconds"}

@registry.register("failing_task")
async def failing_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """A task that always fails, for testing retries."""
    raise ValueError("This task is designed to fail.")
