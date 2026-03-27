from urllib.parse import urlparse
import asyncio

async def is_url_available(url: str, timeout: int = 10) -> bool:
    """ Проверка доступности URL по DNS """
    
    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return False

        loop = asyncio.get_event_loop()
        await loop.getaddrinfo(parsed.hostname, None)
        
        return True
        
    except Exception:
        return False