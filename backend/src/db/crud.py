from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, exc
from datetime import datetime, timezone
import re

from src.db.models import Url 
from src.core.exceptions import URLAlreadyRegistered, SlugAlreadyRegistered

async def write_url(slug: str, long_url: str, ttl: datetime, session: AsyncSession) -> None:
    """Записать обьект ссылки в базу данных"""

    url = Url(
            slug = slug,
            long_url = long_url,
            ttl = ttl
        )
    session.add(url)
    try:
        await session.commit()
        await session.refresh(url)  
        return url 
    except IntegrityError as error:
        await session.rollback()

        try:
            field = re.search(r'Key \((.*?)\)', str(error.orig)).group(1)
        except AttributeError:
            raise error

        if field == "slug":
            raise SlugAlreadyRegistered
        
        if field == "long_url":
            raise URLAlreadyRegistered
        
        raise error

async def get_url(*, slug: str = None, long_url: str = None, session: AsyncSession) -> Url:
    """Получить обьект ссылки по слагу или по длинной ссылке"""
    url = await session.scalar(
        select(Url)
        .where(Url.slug == slug if slug else Url.long_url == long_url)
    )

    if not url: 
        raise exc.NoResultFound
    
    if url.update_is_active():
        await session.commit()

    return url 

async def get_urls(session: AsyncSession) -> list[Url]: # Не используется, но понадобиться в будущем
    """Получить все URL, отсортированные по убыванию кликов."""
    urls = await session.scalars(
        select(Url).order_by(Url.count_clicks.desc())
    )

    urls = list(urls.all())

    need_commit = False
    for url in urls:
        if url.update_is_active():
            need_commit = True
    
    if need_commit:
        await session.commit()

    return urls

async def increase_count_clicks(slug: str, session: AsyncSession) -> None:
    """Изменить количество переходов по слагу на +1"""
    await session.execute(
        update(Url)
        .where(Url.slug == slug)
        .values(count_clicks = Url.count_clicks + 1)
    )
    
    await session.commit()