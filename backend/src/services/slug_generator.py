from sqlalchemy.exc import NoResultFound
import random
import string

from src.api.dependencies import SessionDep, SettingsDep 
from src.db.crud import get_url

def ValidOutputUrl(func):
    async def wrapper(*args, **kwargs):
        url = await func(*args, **kwargs)
        try:
            await get_url(args[0], slug = url)
        except NoResultFound:
            return url
        return await wrapper(*args, **kwargs)
    return wrapper


@ValidOutputUrl
async def create_url(session: SessionDep, settings: SettingsDep, length: int = None) -> str: 
    if not length: length = settings.RANDOM_SLUG_LENGTH

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))