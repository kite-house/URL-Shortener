import pytest
from unittest.mock import Mock, AsyncMock
from redis import Redis

@pytest.fixture
def mock_redis():
    mock = Mock(spec=Redis)
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    return mock

@pytest.fixture(autouse=True)
def patch_redis(monkeypatch, mock_redis):
    monkeypatch.setattr("src.api.shortener.redis_client", mock_redis)
    return mock_redis