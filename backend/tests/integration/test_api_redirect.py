import pytest
from unittest.mock import patch, AsyncMock

class TestRedirectAPI:
    
    @pytest.mark.asyncio
    async def test_redirect_success(self, client, sample_url_data):
        with patch('src.services.url_checker.is_url_available', AsyncMock(return_value=True)):
            create_response = await client.post("/api/shorten", json=sample_url_data)
            slug = create_response.json()["data"]["slug"]
        
        response = await client.get(f"/api/{slug}", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == sample_url_data["url"]
    
    @pytest.mark.asyncio
    async def test_redirect_not_found(self, client):
        response = await client.get("/api/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_redirect_increments_clicks(self, client, sample_url_data):
        with patch('src.services.url_checker.is_url_available', AsyncMock(return_value=True)):
            create_response = await client.post("/api/shorten", json=sample_url_data)
            slug = create_response.json()["data"]["slug"]
        
        for _ in range(10): 
            await client.get(f"/api/{slug}", follow_redirects=False)
        
        info_response = await client.get(f"/api/info/{slug}")
        assert info_response.json()["data"]["count_clicks"] == 10