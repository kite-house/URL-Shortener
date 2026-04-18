from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, exc
from datetime import datetime, timezone
import re

from src.db.models import Url 
from src.core.exceptions import URLAlreadyRegistered, SlugAlreadyRegistered

async def write_url(slug: str, long_url: str, ttl: datetime, session: AsyncSession) -> Url:
    """Записать обьект ссылки в базу данных с возвращением"""

    url = Url(
            slug = slug,
            long_url = long_url,
            ttl = ttl
        )
    
    session.add(url)

    try:
        await session.flush()
        await session.refresh(url)  
        return url 
    except IntegrityError as error:
        try:
            field = re.search(r'Key \((.*?)\)', str(error.orig)).group(1)
        except AttributeError:
            raise

        if field == "slug":
            raise SlugAlreadyRegistered
        
        if field == "long_url":
            raise URLAlreadyRegistered
        
        raise

async def get_url(*, slug: str = None, long_url: str = None, session: AsyncSession) -> Url:
    """Получить обьект ссылки по слагу или по длинной ссылке"""
    url = await session.scalar(
        select(Url)
        .where(Url.slug == slug if slug else Url.long_url == long_url)
    )

    if not url: 
        raise exc.NoResultFound
    
    return url 

async def increase_count_clicks(slug: str, session: AsyncSession) -> None:
    """Изменить количество переходов по слагу на +1"""
    await session.execute(
        update(Url)
        .where(Url.slug == slug)
        .values(count_clicks = Url.count_clicks + 1)
    )