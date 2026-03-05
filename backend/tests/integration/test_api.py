import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestAPI:    
    @pytest.mark.asyncio
    async def test_full_url_flow(self, ac: AsyncClient):
        create_response = await ac.post("/api/shorten", json={"url": "https://example.com"})
        assert create_response.status_code == 201
        slug = create_response.json()["data"]["slug"]
        
        info_response = await ac.get(f"/api/info/{slug}")
        assert info_response.status_code == 200
        assert info_response.json()["data"]["count_clicks"] == 0

        redirect_response = await ac.get(f"/api/{slug}", follow_redirects=False)
        assert redirect_response.status_code == 302

        info_response = await ac.get(f"/api/info/{slug}")
        assert info_response.json()["data"]["count_clicks"] == 1
    
    @pytest.mark.asyncio
    async def test_create_short_url(self, ac: AsyncClient):
        response = await ac.post("/api/shorten", json={"url": "https://test.com"})
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "slug" in data["data"]
    
    @pytest.mark.asyncio
    async def test_create_duplicate_url(self, ac: AsyncClient):
        url = "https://duplicate.com"
        response1 = await ac.post("/api/shorten", json={"url": url})
        assert response1.status_code == 201
        
        response2 = await ac.post("/api/shorten", json={"url": url})
        assert response2.status_code == 208
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_info(self, ac: AsyncClient):
        response = await ac.get("/api/info/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_redirect_nonexistent(self, ac: AsyncClient):
        response = await ac.get("/api/nonexistent", follow_redirects=False)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_top_urls(self, ac: AsyncClient):
        for i in range(3):
            await ac.post("/api/shorten", json={"url": f"https://top{i}.com"})
        
        response = await ac.get("/api/top")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3