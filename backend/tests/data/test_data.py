from datetime import datetime, timedelta

VALID_URLS = [
    "https://example.com",
    "https://test.ru",
    "http://localhost:8000",
    "https://sub.domain.com/path?param=value",
    "https://very-long-domain-name-with-many-parts.com/very/long/path/with/many/segments"
]

INVALID_URLS = [
    "not-a-url",
    "ftp://example.com",
    "http://",
    "https://",
    "javascript:alert(1)",
    "data:text/html,<script>",
    "file:///etc/passwd",
    "www.example.com",  
    "example.com",      
]

TEST_SLUGS = {
    "valid": ["abc123", "test", "my-slug", "valid123", "short"],
    "invalid": ["test/", "test?", "test@", "test#", "test space", "test\n"],
    "reserved": ["info", "top", "shorten", "api", "docs", "redoc"],
    "too_short": ["a", "ab"],
    "too_long": ["a" * 51] 
}

TEST_LENGTHS = {
    "min": 3,
    "max": 20,
    "default": 6,
    "invalid": [0, 1, 2, 21, 22, 100]
}

TEST_URL_OBJECTS = [
    {
        "slug": "most-popular",
        "long_url": "https://popular.com",
        "count_clicks": 100,
        "date_created": datetime.now() - timedelta(days=30)
    },
    {
        "slug": "medium-popular",
        "long_url": "https://medium.com",
        "count_clicks": 50,
        "date_created": datetime.now() - timedelta(days=15)
    },
    {
        "slug": "least-popular",
        "long_url": "https://least.com",
        "count_clicks": 10,
        "date_created": datetime.now() - timedelta(days=5)
    },
    {
        "slug": "new",
        "long_url": "https://new.com",
        "count_clicks": 0,
        "date_created": datetime.now()
    }
]

def get_test_url_data():
    return TEST_URL_OBJECTS.copy()

def get_valid_slug():
    return TEST_SLUGS["valid"][0]

def get_invalid_slugs():
    return TEST_SLUGS["invalid"] + TEST_SLUGS["reserved"]