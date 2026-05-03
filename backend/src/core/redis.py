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
        return await self.client.get(key)
    
    async def setex(self, key: str, ttl: int, value: str) -> bool:
        """Установка значения с временем жизни (TTL в секундах)"""
        return await self.client.setex(key, ttl, value)
    
    async def ping(self) -> bool:
        """Проверка доступности Redis"""
        return await self.client.ping()
    
    async def close(self) -> None:
        """Закрытие соединения с Redis"""
        await self.client.close()
    
    async def delete(self, key: str) -> bool:
        """Удаление ключа"""
        return await self.client.delete(key) > 0
    
    async def hdel(self, key: str, field: str) -> int:
        """Удаление поля в хэше"""
        return await self.client.hdel(key, field)
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        return await self.client.exists(key) > 0
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Увеличение значения ключа"""
        return await self.client.incr(key, amount)
    
    async def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        """Увеличение значения поля в хэше"""
        return await self.client.hincrby(key, field, amount)
    
    async def hscan(self, key: str, cursor: int, count: int = 100) -> Tuple[int, Dict[str, str]]:
        """ Итеративный обход хэша без блокировки."""
        return await self.client.hscan(key, cursor, count=count)
    