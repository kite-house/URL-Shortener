from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, exc
from datetime import datetime, timezone
import re

from src.db.models import Url 
from src.core.exceptions import URLAlreadyRegistered, SlugAlreadyRegistered
from src.core.logging import logger

async def write_url(session: AsyncSession, slug: str, long_url: str, ttl: datetime) -> Url:
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
        await session.rollback()
        try:
            field = re.search(r'Key \((.*?)\)', str(error.orig)).group(1)
        except AttributeError:
            raise

        if field == "slug":
            raise SlugAlreadyRegistered
        
        if field == "long_url":
            raise URLAlreadyRegistered
        
        raise

async def get_url(session: AsyncSession, slug: str = None, long_url: str = None) -> Url:
    """Получить обьект ссылки по слагу или по длинной ссылке"""
    url = await session.scalar(
        select(Url)
        .where(Url.slug == slug if slug else Url.long_url == long_url)
    )

    if not url: 
        raise exc.NoResultFound
    
    return url 

async def increment_count_clicks(session: AsyncSession, slug: str, count_clicks: int) -> None:
    """Увеличить количество переходов"""
    await session.execute(
        update(Url)
        .where(Url.slug == slug)
        .values(count_clicks = Url.count_clicks + count_clicks)
    )