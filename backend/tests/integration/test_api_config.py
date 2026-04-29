import pytest

class TestConfigAPI:
    
    @pytest.mark.asyncio
    async def test_get_slug_length(self, client, test_settings):
        response = await client.get("/api/config/slug-length")
        assert response.status_code == 200
        data = response.json()
        assert data["slug_min_length"] == test_settings.SLUG_MIN_LENGTH
        assert data["slug_max_length"] == test_settings.SLUG_MAX_LENGTH
    
    @pytest.mark.asyncio
    async def test_get_frontend_config(self, client, test_settings):
        response = await client.get("/api/config/frontend")
        assert response.status_code == 200
        data = response.json()
        assert data["app_name"] == test_settings.APP_NAME
        assert data["version"] == test_settings.VERSION