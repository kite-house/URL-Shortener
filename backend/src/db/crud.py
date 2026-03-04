from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, exc
from datetime import datetime

from src.db.models import Url 
from src.core.exceptions import URLAlreadyRegistered

async def write_url(slug: str, long_url: str, session: AsyncSession) -> None:
    """Записать обьект ссылки в базу данных"""
    session.add(
        Url(
            slug = slug,
            long_url = long_url,
            date_created = datetime.now().date()
        )
    )
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise URLAlreadyRegistered

async def get_url(*, slug: str = None, long_url: str = None, session: AsyncSession) -> Url:
    """Получить обьект ссылки по слагу"""
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
    
    await session.commit()

async def get_urls(session: AsyncSession) -> list[Url]:
    """Получить все URL, отсортированные по убыванию кликов."""
    result = await session.scalars(
        select(Url).order_by(Url.count_clicks.desc())
    )
    return list(result.all())