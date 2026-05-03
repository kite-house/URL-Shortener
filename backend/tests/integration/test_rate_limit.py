# backend/tests/integration/test_rate_limit.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.core.config import settings
from src.core.redis import RedisService


@pytest.fixture
async def rate_limit_client(db_session, test_settings):
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi_easylimiter import RateLimitMiddleware
    from src.api.shortener import router as shortener_router
    from src.api.configuration import router as configuration_router
    from src.api.dependencies import get_session, get_settings, get_redis_service
    
    test_app = FastAPI()
    
    @test_app.get("/ping")
    async def ping():
        return {"status": "ok"}
    
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    redis_service = RedisService(test_settings, db=2)
    await redis_service.client.flushdb()
    
    test_app.add_middleware(
        RateLimitMiddleware,
        redis=redis_service.client,
        rules={
            "/*": (5, 60, "moving"),              # 5 запросов/мин (для быстрого теста)
            "/api/shorten": (3, 60, "fixed"),     # 3 запроса/мин
        },
        ban_offenses=2,                           # Бан после 2 нарушений
        ban_length="1m",
        site_ban=True,
    )
    
    test_app.include_router(shortener_router)
    test_app.include_router(configuration_router)
    
    async def override_get_session():
        yield db_session
    
    async def override_get_settings():
        yield test_settings
    
    test_app.dependency_overrides[get_session] = override_get_session
    test_app.dependency_overrides[get_settings] = override_get_settings
    test_app.dependency_overrides[get_redis_service] = lambda: redis_service
    
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    await redis_service.client.flushdb()
    await redis_service.close()
    test_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_rate_limit_global(rate_limit_client):
    results = []
    for i in range(7):
        resp = await rate_limit_client.get("/ping")
        results.append(resp.status_code)
    
    for i in range(5):
        assert results[i] == 200 
    assert results[5] in (429, 403)
    assert results[6] in (429, 403)


@pytest.mark.asyncio
async def test_rate_limit_ban(rate_limit_client):
    results = []
    
    for _ in range(15):
        resp = await rate_limit_client.post(
            "/api/shorten",
            json={"original_url": "https://any-url.com/test"}
        )
        results.append(resp.status_code)
        if 403 in results:
            break
    
    assert 403 in results