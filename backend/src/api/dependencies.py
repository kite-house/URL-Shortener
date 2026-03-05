from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated

from src.db.db import async_session
from src.core.config import Settings
from src.core.redis import RedisService

# ====== SESSION DB ======
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# ====== SETTINGS ======
async def get_settings() -> AsyncGenerator[Settings, None]:
    settings = Settings()
    yield settings

SettingsDep = Annotated[Settings, Depends(get_settings)]

# ====== REDIS ======
async def get_redis_service(settings: SettingsDep) -> AsyncGenerator[RedisService, None]:
    redis_service = RedisService(settings)
    try:
        await redis_service.client.ping()
        yield redis_service
    finally:
        await redis_service.close()

RedisDep = Annotated[RedisService, Depends(get_redis_service)]