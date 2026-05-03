from redis.asyncio import Redis as AsyncRedis
from typing import Optional, Tuple, Dict

from src.core.config import Settings
from src.core.logging import logger


class RedisService:
    def __init__(self, settings: Settings, db: int = 0):
        self.settings = settings
        self.client = AsyncRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=db,
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[str]:
        """Получение значения по ключу"""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get failed for key {key}: {e}")
            return None

    async def setex(self, key: str, ttl: int, value: str) -> bool:
        """Установка значения с временем жизни (TTL в секундах)"""
        try:
            return await self.client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis setex failed for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Удаление ключа"""
        try:
            return await self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return False

    async def hdel(self, key: str, field: str) -> int:
        """Удаление поля в хэше"""
        try:
            return await self.client.hdel(key, field)
        except Exception as e:
            logger.error(f"Redis hdel failed for key {key} field {field}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists failed for key {key}: {e}")
            return False

    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Увеличение значения ключа"""
        try:
            return await self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis incr failed for key {key}: {e}")
            return None

    async def hincrby(self, key: str, field: str, amount: int = 1) -> Optional[int]:
        """Увеличение значения поля в хэше"""
        try:
            return await self.client.hincrby(key, field, amount)
        except Exception as e:
            logger.error(f"Redis hincrby failed for key {key} field {field}: {e}")
            return None

    async def hscan(self, key: str, cursor: int, count: int = 100) -> Tuple[int, Dict[str, str]]:
        """Итеративный обход хэша без блокировки"""
        try:
            return await self.client.hscan(key, cursor, count=count)
        except Exception as e:
            logger.error(f"Redis hscan failed for key {key}: {e}")
            return (0, {})

    async def ping(self) -> bool:
        """Проверка доступности Redis"""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def close(self) -> None:
        """Закрытие соединения с Redis"""
        try:
            await self.client.close()
        except Exception as e:
            logger.error(f"Redis close failed: {e}")
        