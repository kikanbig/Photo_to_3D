"""
Redis client configuration
"""
import redis.asyncio as redis
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

redis_client = None

async def init_redis():
    """Initialize Redis client"""
    global redis_client
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize Redis", error=str(e))
        raise

async def get_redis():
    """Get Redis client"""
    return redis_client
