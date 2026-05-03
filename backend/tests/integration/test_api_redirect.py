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
    async def test_redirect_increments_clicks(self, client, sample_url_data, real_redis, db_session):
        with patch('src.services.url_checker.is_url_available', AsyncMock(return_value=True)):
            create_response = await client.post("/api/shorten", json=sample_url_data)
            slug = create_response.json()["data"]["slug"]
        
        for _ in range(10): 
            await client.get(f"/api/{slug}", follow_redirects=False)
        
        from src.db.crud import increment_count_clicks
        
        counters = await real_redis.client.hgetall("counter_transmissions")
        for key, value in counters.items():
            await increment_count_clicks(db_session, key, int(value))
        await db_session.commit()
        await real_redis.delete("counter_transmissions")
        
        info_response = await client.get(f"/api/info/{slug}")
        assert info_response.json()["data"]["count_clicks"] == 10