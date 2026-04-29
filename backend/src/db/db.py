from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

engine = create_async_engine(
    url = settings.DB_URL,     
    pool_size=100,         
    max_overflow=100,      
    pool_pre_ping=True,   
    pool_recycle=3600
)
async_session = async_sessionmaker(engine, autoflush=True, expire_on_commit=False)
