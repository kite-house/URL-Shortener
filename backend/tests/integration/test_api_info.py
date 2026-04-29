import pytest
from unittest.mock import patch, AsyncMock

class TestInfoAPI:
    
    @pytest.mark.asyncio
    async def test_info_existing_slug(self, client, sample_url_data):
        with patch('src.services.url_checker.is_url_available', AsyncMock(return_value=True)):
            create_response = await client.post("/api/shorten", json=sample_url_data)
            slug = create_response.json()["data"]["slug"]
        
        response = await client.get(f"/api/info/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["slug"] == slug
    
    @pytest.mark.asyncio
    async def test_info_nonexistent_slug(self, client):
        response = await client.get("/api/info/nonexistent")
        assert response.status_code == 404
        assert response.json()["data"]["slug"] == "nonexistent"