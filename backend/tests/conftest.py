# conftest.py - упрощённая версия
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import os
from typing import AsyncGenerator, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import patch, AsyncMock

from src.main import app
from src.db import models
from src.core.config import Settings
from src.core.redis import RedisService
from src.api.dependencies import get_session, get_settings, get_redis_service

DB_USER = os.getenv("DB_USER", "test_postgres")
DB_PASS = os.getenv("DB_PASS", "test_postgres")
DB_HOST = os.getenv("DB_HOST", "test_postgres_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test_postgres_db")

TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

REDIS_HOST = os.getenv("REDIS_HOST", "test_cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")


@pytest.fixture
def test_settings():
    class TestSettings(Settings):
        @property
        def DB_URL(self):
            return TEST_DATABASE_URL
    
    settings = TestSettings()
    settings.MODE = "TEST"
    settings.REDIS_CACHE_TTL = 60
    settings.SLUG_MIN_LENGTH = 3
    settings.SLUG_MAX_LENGTH = 10
    settings.REDIS_HOST = REDIS_HOST
    settings.REDIS_PORT = REDIS_PORT
    settings.REDIS_PASSWORD = REDIS_PASSWORD
    settings.API_BASE_URL = "http://localhost:8000"
    return settings


@pytest.fixture
async def engine(test_settings):
    print(f"Connecting to: {test_settings.DB_URL}")
    engine = create_async_engine(test_settings.DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def real_redis(test_settings):
    redis = RedisService(test_settings)
    await redis.client.flushdb() 
    yield redis
    await redis.client.flushdb() 
    await redis.close()


@pytest.fixture
async def client(db_session, test_settings, real_redis):
    """Клиент с реальным Redis"""
    async def override_get_session():
        yield db_session
    
    async def override_get_settings():
        yield test_settings
    
    async def override_get_redis():
        yield real_redis
    
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_redis_service] = override_get_redis
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    redis = AsyncMock(spec=RedisService)
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.ping = AsyncMock(return_value=True)
    redis.hincrby = AsyncMock(return_value=1)
    redis.hdel = AsyncMock(return_value=1)
    redis.hget = AsyncMock(return_value=None)
    redis.hgetall = AsyncMock(return_value={})
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    redis.incr = AsyncMock(return_value=1)
    redis.close = AsyncMock()
    return redis


@pytest.fixture
def sample_url_data() -> Dict:
    return {"url": "https://example.com/very/long/url"}