import pytest
from unittest.mock import patch, AsyncMock

class TestE2EWorkflow:
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, client, real_redis, db_session):
        original_url = "https://example.com/very/long/path"

        with patch('src.services.url_checker.is_url_available', AsyncMock(return_value=True)):
            create_response = await client.post("/api/shorten", json={"url": original_url})
            assert create_response.status_code == 201
            slug = create_response.json()["data"]["slug"]

        info_response = await client.get(f"/api/info/{slug}")
        assert info_response.status_code == 200
        assert info_response.json()["data"]["count_clicks"] == 0

        for _ in range(10):
            redirect_response = await client.get(f"/api/{slug}", follow_redirects=False)
            assert redirect_response.status_code == 302
            assert redirect_response.headers["location"] == original_url

        from src.db.crud import increment_count_clicks
        
        counters = await real_redis.client.hgetall("counter_transmissions")
        for key, value in counters.items():
            await increment_count_clicks(db_session, key, int(value))
        await db_session.commit()
        await real_redis.delete("counter_transmissions")

        info_response2 = await client.get(f"/api/info/{slug}")
        assert info_response2.json()["data"]["count_clicks"] == 10
        
    @pytest.mark.asyncio
    async def test_custom_slug_workflow(self, client):
        custom_slug = "mycustom"
        original_url = "https://example.com/test"
        
        with patch('src.services.url_checker.is_url_available', AsyncMock(return_value=True)):
            response = await client.post(f"/api/shorten?custom_slug={custom_slug}", json={"url": original_url})
            assert response.status_code == 201
            assert response.json()["data"]["slug"] == custom_slug
        
        redirect_response = await client.get(f"/api/{custom_slug}", follow_redirects=False)
        assert redirect_response.status_code == 302