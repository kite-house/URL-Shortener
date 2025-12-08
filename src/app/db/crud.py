from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, update, exc
from datetime import datetime
import os

from db.models import Base, Url 

DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASS = os.environ.get('DATABASE_PASS')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
DATABASE_NAME = os.environ.get('DATABASE_NAME')


engine = create_async_engine(
    url = f"mysql+aiomysql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

async_session = async_sessionmaker(engine)

async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def write_url(slug: str, long_url: str) -> None:
    async with async_session() as session:
        session.add(
            Url(
                slug = slug,
                long_url = long_url,
                date_created = datetime.now().date()
            )
        )

        await session.commit()

async def get_url(*, slug: str = None, long_url: str = None) -> Url:
    async with async_session() as session:
        url = await session.scalar(
            select(Url)
            .where(Url.slug == slug if slug else Url.long_url == long_url)
        )

        if not url: 
            raise exc.NoResultFound
        
        return url

async def increase_count_clicks(slug: str) -> None:
    async with async_session() as session:
        await session.execute(
            update(Url)
            .where(Url.slug == slug)
            .values(number_clicks = Url.count_clicks + 1)
        )
        
        await session.commit()