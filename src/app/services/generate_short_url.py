import random
import string
from dataclasses import dataclass

from db.crud import get_url

@dataclass
class UrlLength:
    MAX_LENGTH: int = 9
    MIN_LENGTH: int = 5

    @classmethod
    def get(cls) -> int:
        return random.randint(cls.MIN_LENGTH, cls.MAX_LENGTH)

def ValidOutputUrl(func):
    async def wrapper(*args, **kwargs):
        url = await func(*args, **kwargs)
        try:
            await get_url(url)
        except ValueError:
            return url
        return await wrapper(*args, **kwargs)
    return wrapper


@ValidOutputUrl
async def create_url() -> str: # Url
    return "".join(random.choices(string.ascii_letters, k=UrlLength.get()))