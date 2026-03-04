from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.shortener import router as shortener_router
from src.db.db import engine
from src.db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(
    title = 'URL-Shortener',
    summary= "Сервис для сокращения ссылок",
    description = 'Сервис для сокращения ссылок и перенаправления пользователей с сокращенной ссылки на внешний адрес',
    version = "2.0.3",
    lifespan=lifespan
)

app.include_router(shortener_router)
