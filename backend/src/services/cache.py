from typing import Optional

from src.core.redis import RedisService
from src.core.logging import logger

async def cache_url(
    redis: RedisService,  
    slug: str, 
    url: str, 
    ttl: int = 86400
) -> None:
    """Фоновая задача для кэширования URL в Redis"""
    try:
        await redis.setex(slug, ttl, url)
    except Exception as e:
        logger.error(str(e))


async def get_cached_url(
    redis: RedisService,
    slug: str
) -> Optional[str]:
    """Получение URL из кэша"""
    try:
        return await redis.get(slug)
    except Exception as e:
        logger.error(str(e))
        return None