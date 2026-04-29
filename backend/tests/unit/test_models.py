from datetime import datetime, timedelta, timezone
from src.db.models import Url

class TestUrlModel:
    
    def test_update_is_active_no_ttl(self):
        url = Url(is_active=True, ttl=None)
        assert url.update_is_active() is True
        assert url.is_active is True
    
    def test_update_is_active_with_future_ttl(self):
        future_ttl = datetime.now(timezone.utc) + timedelta(days=7)
        url = Url(is_active=True, ttl=future_ttl)
        assert url.update_is_active() is True
        assert url.is_active is True
    
    def test_update_is_active_expired_ttl(self):
        expired_ttl = datetime.now(timezone.utc) - timedelta(days=1)
        url = Url(is_active=True, ttl=expired_ttl)
        assert url.update_is_active() is False
        assert url.is_active is False
    
    def test_update_is_active_already_inactive(self):
        expired_ttl = datetime.now(timezone.utc) - timedelta(days=1)
        url = Url(is_active=False, ttl=expired_ttl)
        assert url.update_is_active() is False
        assert url.is_active is False