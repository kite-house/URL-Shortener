from typing import Optional, Tuple

import aiohttp

async def is_url_available(url: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.head(url, allow_redirects=True, ssl=False) as response:
                if response.status < 400:
                    return True
                
                else:
                    return False
                    
    except Exception:
        return False