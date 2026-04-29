import pytest
from unittest.mock import patch, AsyncMock
from src.services.url_checker import is_url_available

class TestURLChecker:
    
    @pytest.mark.asyncio
    async def test_valid_url(self):
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.getaddrinfo = AsyncMock(return_value=True)
            result = await is_url_available("https://example.com")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_invalid_url_format(self):
        result = await is_url_available("not-a-url")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_empty_url(self):
        result = await is_url_available("")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_dns_resolution_error(self):
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.getaddrinfo = AsyncMock(side_effect=Exception("DNS error"))
            result = await is_url_available("https://nonexistent.com")
            assert result is False