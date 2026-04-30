from typing import Optional

from src.core.redis import RedisService
from src.core.logging import logger

async def cache_url(redis: RedisService, slug: str, url: str, ttl: int = 86400) -> None:
    """Фоновая задача для кэширования URL в Redis"""
    try:
        await redis.setex(slug, ttl, url)
    except Exception as e:
        logger.error(str(e))


async def get_cached_url(redis: RedisService, slug: str) -> Optional[str]:
    """Получение URL из кэша"""
    try:
        return await redis.get(slug)
    except Exception as e:
        logger.error(str(e))
        return None
    
async def accum_link_increment(redis: RedisService, slug) -> Optional[int]:
    """ Накопление пула счетчиков переходов по ссылкам """
    try:
        return await redis.hincrby("counter_transmissions", slug)
    except Exception as e:
        logger.error(str(e))
        return None
    
async def clear_accum_link_incremet(redis: RedisService, slug) -> None:
    """ Очищение счетчика переходов по ссылке"""
    try:
        await redis.hdel("counter_transmissions", slug)
    except Exception as e:
        logger.error(str(e))
        return None
