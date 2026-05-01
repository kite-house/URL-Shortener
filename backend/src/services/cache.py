import json
from typing import Optional
from datetime import datetime, timezone

from src.core.redis import RedisService
from src.core.logging import logger

async def cache_url(redis: RedisService, slug: str, url: str, expires_at: datetime, ttl: int = 86400) -> None:
    """Фоновая задача для кэширования URL в Redis"""
    try:
        cache_data = {
            "long_url": url, 
            "expires_at": expires_at.isoformat() if expires_at else None
        }
        await redis.setex(slug, ttl, json.dumps(cache_data))
    except Exception as e:
        logger.error(str(e))

async def get_cached_url(redis: RedisService, slug: str) -> tuple[str | None, bool]:
    """Получить URL из кэша с проверкой срока действия"""
    try:
        cached = await redis.get(slug)
        if cached:
            data = json.loads(cached)
            if data.get("expires_at"):
                expires_at = datetime.fromisoformat(data["expires_at"])
                if expires_at and expires_at < datetime.now(timezone.utc):
                    await redis.delete(slug, cached)
                    return None, False
            return data["long_url"], True
        return None, False
    except Exception as e:
        logger.error(str(e))
        return None, False
    
async def increment_click_counter(redis: RedisService, slug) -> Optional[int]:
    """Увеличить счётчик кликов, вернуть новое значение"""
    try:
        return await redis.hincrby("counter_transmissions", slug)
    except Exception as e:
        logger.error(str(e))
        return None
    
async def reset_click_counter(redis: RedisService, slug: str) -> None:
    """Сбросить счётчик кликов для слага"""
    try:
        await redis.hdel("counter_transmissions", slug)
    except Exception as e:
        logger.error(str(e))
        return None
