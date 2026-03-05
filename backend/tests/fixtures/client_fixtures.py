import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.api.dependencies import get_session
from src.db.db import settings

@pytest.fixture
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