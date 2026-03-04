import redis.asyncio as redis
from app.core.config import settings

# Create a global redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URI,
    decode_responses=True,
)

def get_redis_client() -> redis.Redis:
    """Get a redis client instance attached to the global pool."""
    return redis.Redis(connection_pool=redis_pool)
