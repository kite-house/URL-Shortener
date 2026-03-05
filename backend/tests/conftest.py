"""Главный конфигурационный файл для тестов."""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.api.dependencies import get_session
from src.core.config import settings

from tests.fixtures.db_fixtures import event_loop, engine, db_session, setup_database
from tests.fixtures.redis_fixtures import mock_redis, patch_redis

@pytest.fixture(scope="function")
async def ac(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function", autouse=True)
def setup_test_settings():
    settings.BASE_URL = "http://test"
    settings.MODE = "TEST"
    yield