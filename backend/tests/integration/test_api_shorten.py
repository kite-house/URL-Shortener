import pytest
from unittest.mock import patch, AsyncMock

class TestShortenAPI:
    
    @pytest.mark.asyncio
    async def test_shorten_url_success(self, client, sample_url_data):
        with patch('src.api.shortener.is_url_available', AsyncMock(return_value=True)):
            response = await client.post("/api/shorten", json=sample_url_data)
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert "slug" in data["data"]
    
    @pytest.mark.asyncio
    async def test_shorten_url_with_custom_slug(self, client, sample_url_data):
        custom_slug = "mycustom"
        with patch('src.api.shortener.is_url_available', AsyncMock(return_value=True)):
            response = await client.post(f"/api/shorten?custom_slug={custom_slug}", json=sample_url_data)
            assert response.status_code == 201
            assert response.json()["data"]["slug"] == custom_slug
    
    @pytest.mark.asyncio
    async def test_shorten_url_with_ttl(self, client, sample_url_data):
        with patch('src.api.shortener.is_url_available', AsyncMock(return_value=True)):
            response = await client.post("/api/shorten?ttl_days=30", json=sample_url_data)
            assert response.status_code == 201
            assert response.json()["data"]["ttl"] is not None
    
    @pytest.mark.asyncio
    async def test_shorten_url_unavailable(self, client, sample_url_data):
        with patch('src.api.shortener.is_url_available', AsyncMock(return_value=False)):
            response = await client.post("/api/shorten", json=sample_url_data)
            assert response.status_code == 422
            assert "недоступна" in response.text
        
    @pytest.mark.asyncio
    async def test_shorten_invalid_url_format(self, client):
        response = await client.post("/api/shorten", json={"url": "not-a-url"})
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_shorten_with_length_param(self, client, sample_url_data):
        with patch('src.api.shortener.is_url_available', AsyncMock(return_value=True)):
            response = await client.post("/api/shorten?length=8", json=sample_url_data)
            assert response.status_code == 201
            assert len(response.json()["data"]["slug"]) == 8