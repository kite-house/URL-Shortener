from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from src.db.db import async_session
from src.core.config import Settings

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_settings() -> AsyncGenerator[Settings, None]:
    settings = Settings()
    yield settings
    