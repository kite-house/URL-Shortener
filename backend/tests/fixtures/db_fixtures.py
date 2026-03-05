import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.pool import NullPool

from src.core.config import settings
from src.db.models import Base

@pytest.fixture(scope="function")  
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.DB_URL,
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    async with async_session() as session:
        yield session
        await session.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)