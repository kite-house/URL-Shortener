from redis.asyncio import Redis as AsyncRedis
from src.core.config import Settings
from src.core.logging import logger


class RedisService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    async def get(self, key: str) -> str | None:
        return await self.client.get(key)
    
    async def setex(self, key: str, time: int, value: str) -> bool:
        return await self.client.setex(key, time, value)
    
    async def ping(self) -> bool:
        """Проверка соединения с Redis"""
        return await self.client.ping()
    
    
    async def close(self):
        """Закрытие соединения"""
        await self.client.close()
    
    async def delete(self, key: str) -> bool:
        """Удаление ключа из Redis"""
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        return await self.client.exists(key) > 0