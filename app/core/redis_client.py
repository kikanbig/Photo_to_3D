"""
Redis client configuration
"""
import structlog

from app.core.config_v1 import settings

logger = structlog.get_logger(__name__)

redis_client = None

class MockRedis:
    """Mock Redis client for development"""
    def __init__(self):
        self._storage = {}
    
    async def ping(self):
        return True
    
    async def set(self, key, value):
        self._storage[key] = value
        return True
    
    async def get(self, key):
        return self._storage.get(key)
    
    async def delete(self, key):
        return self._storage.pop(key, None) is not None

async def init_redis():
    """Initialize Redis client"""
    global redis_client
    try:
        if settings.REDIS_URL.startswith("redis://localhost"):
            # Use mock Redis for local development
            redis_client = MockRedis()
            await redis_client.ping()
            logger.info("Mock Redis initialized successfully (development mode)")
        else:
            # Use real Redis
            import redis.asyncio as redis
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            logger.info("Redis initialized successfully")
    except Exception as e:
        logger.warning("Redis not available, using mock client", error=str(e))
        redis_client = MockRedis()

async def get_redis():
    """Get Redis client"""
    return redis_client
