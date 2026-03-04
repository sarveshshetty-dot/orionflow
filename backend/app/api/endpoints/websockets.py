import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import get_redis_client
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    redis = get_redis_client()
    pubsub = redis.pubsub()
    
    # Subscribe to different real-time channels
    tasks_channel = f"{settings.LOGS_CHANNEL_PREFIX}:tasks"
    runs_channel = f"{settings.LOGS_CHANNEL_PREFIX}:runs"
    
    await pubsub.subscribe(tasks_channel, runs_channel)
    logger.info("WebSocket client connected to logs channel.")

    try:
        while True:
            # We can use get_message in a loop with sleep, or asyncio sleep
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await websocket.send_text(data)
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await pubsub.unsubscribe()
        await pubsub.close()
