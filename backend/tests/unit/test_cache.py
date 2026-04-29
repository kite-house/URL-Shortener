import pytest
from unittest.mock import AsyncMock
from src.services.cache import cache_url, get_cached_url

class TestCache:
    
    @pytest.mark.asyncio
    async def test_cache_url_success(self, mock_redis):
        await cache_url(mock_redis, "abc123", "https://example.com", ttl=3600)
        mock_redis.setex.assert_called_once_with("abc123", 3600, "https://example.com")
    
    @pytest.mark.asyncio
    async def test_cache_url_redis_error(self, mock_redis):
        mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))
        await cache_url(mock_redis, "abc123", "https://example.com")
    
    @pytest.mark.asyncio
    async def test_get_cached_url_found(self):
        redis = AsyncMock()
        redis.get = AsyncMock(return_value="https://example.com")
        result = await get_cached_url(redis, "abc123")
        assert result == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_get_cached_url_not_found(self, mock_redis):
        mock_redis.get = AsyncMock(return_value=None)
        result = await get_cached_url(mock_redis, "nonexistent")
        assert result is None