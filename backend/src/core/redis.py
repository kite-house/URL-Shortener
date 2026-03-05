from redis.asyncio import Redis as AsyncRedis
from src.core.config import Settings

class RedisService:
    def __init__(self, settings: Settings):
        self.client = AsyncRedis( 
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    
    async def get(self, key: str) -> str | None:
        return await self.client.get(key)
    
    async def setex(self, key: str, time: int, value: str) -> bool:
        return await self.client.setex(key, time, value)
    
    async def close(self):
        await self.client.close()