from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
import pytest

from src.app.main import app
from src.app.db.db import settings
from src.app.db.models import Base
from src.app.dependencies import get_session

engine = create_async_engine(url = settings.DB_URL)

async_session = async_sessionmaker(engine, autoflush=True, expire_on_commit=False)

@pytest.fixture(scope = 'session', autouse = True)
async def setup_db():
    assert settings.MODE == 'TEST'

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope = 'session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport = ASGITransport(app=app), base_url = "http://test") as ac: 
        yield ac     

