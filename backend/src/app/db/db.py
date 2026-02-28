from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.app.db.config import settings

engine = create_async_engine(url = settings.DB_URL)

async_session = async_sessionmaker(engine, autoflush=True, expire_on_commit=False)
