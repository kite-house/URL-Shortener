import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch, Mock
from sqlalchemy.exc import NoResultFound

from src.services.cache import cache_url, get_cached_url


class TestCache:
    
    @pytest.mark.asyncio
    async def test_cache_url_success(self, mock_redis):
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        await cache_url(mock_redis, "abc123", "https://example.com", expires_at, ttl=3600)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        assert call_args[0] == "abc123"
        assert call_args[1] == 3600
        
        cached_data = json.loads(call_args[2])
        assert cached_data["long_url"] == "https://example.com"
        assert cached_data["expires_at"] == expires_at.isoformat()
    
    @pytest.mark.asyncio
    async def test_cache_url_without_expiry(self, mock_redis):
        await cache_url(mock_redis, "abc123", "https://example.com", None, ttl=3600)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        cached_data = json.loads(call_args[2])
        assert cached_data["long_url"] == "https://example.com"
        assert cached_data["expires_at"] is None
    
    @pytest.mark.asyncio
    async def test_cache_url_redis_error(self, mock_redis):
        mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))
        await cache_url(mock_redis, "abc123", "https://example.com", None)
    
    @pytest.mark.asyncio
    async def test_get_cached_url_found_and_valid(self):
        redis = AsyncMock()
        expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        cached_data = json.dumps({
            "long_url": "https://example.com",
            "expires_at": expires_at
        })
        redis.get = AsyncMock(return_value=cached_data)
        
        result, is_valid = await get_cached_url(redis, "abc123")
        
        assert result == "https://example.com"
        assert is_valid is True
        redis.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_cached_url_expired(self):
        redis = AsyncMock()
        expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        cached_data = json.dumps({
            "long_url": "https://example.com",
            "expires_at": expires_at
        })
        redis.get = AsyncMock(return_value=cached_data)
        
        result, is_valid = await get_cached_url(redis, "abc123")
        
        assert result is None
        assert is_valid is False
        redis.delete.assert_called_once_with("abc123")
    
    @pytest.mark.asyncio
    async def test_get_cached_url_not_found(self, mock_redis):
        mock_redis.get = AsyncMock(return_value=None)
        
        result, is_valid = await get_cached_url(mock_redis, "nonexistent")
        
        assert result is None
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_get_cached_url_invalid_json(self, mock_redis):
        mock_redis.get = AsyncMock(return_value="invalid json")
        
        result, is_valid = await get_cached_url(mock_redis, "abc123")
        
        assert result is None
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_get_cached_url_missing_long_url(self, mock_redis):
        cached_data = json.dumps({"expires_at": None})
        mock_redis.get = AsyncMock(return_value=cached_data)
        
        result, is_valid = await get_cached_url(mock_redis, "abc123")
        
        assert result is None
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_get_cached_url_redis_error(self, mock_redis):
        mock_redis.get = AsyncMock(side_effect=Exception("Connection error"))
        
        result, is_valid = await get_cached_url(mock_redis, "abc123")
        
        assert result is None
        assert is_valid is False


class TestRedirectEndpoint:
    
    @pytest.mark.asyncio
    async def test_redirect_from_cache_valid(self, client, db_session, test_settings, real_redis):
        from src.services.cache import cache_url
        
        slug = "abc123"
        long_url = "https://example.com"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        create_response = await client.post("api/shorten", json={
            "url": long_url,
            "custom_slug": slug,
            "ttl": expires_at.isoformat()
        })
        assert create_response.status_code == 201
        
        await cache_url(real_redis, slug, long_url, expires_at, ttl=3600)
        
        response = await client.get(f"api/{slug}", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == long_url
    
    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client_with_mock_redis, mock_redis):
        slug = "notfound"
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.hincrby = AsyncMock(return_value=1)
        
        with patch('src.db.crud.get_url', new_callable=AsyncMock) as mock_get_url:
            mock_get_url.side_effect = NoResultFound()
            
            response = await client_with_mock_redis.get(f"/{slug}")
            
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_redirect_from_cache_expired(self, client_with_mock_redis, mock_redis):
        slug = "expired123"
        expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        cached_data = json.dumps({
            "long_url": "https://old-example.com",
            "expires_at": expires_at
        })
        
        mock_redis.get = AsyncMock(return_value=cached_data)
        mock_redis.delete = AsyncMock()
        mock_redis.hincrby = AsyncMock(return_value=1)
        
        with patch('src.db.crud.get_url', new_callable=AsyncMock) as mock_get_url:
            mock_get_url.side_effect = NoResultFound()
            
            response = await client_with_mock_redis.get(f"/{slug}")
            
            assert response.status_code == 404