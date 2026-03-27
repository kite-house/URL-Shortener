from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import settings

from src.api.shortener import router as shortener_router
from src.api.configuration import router as configuration_router
from src.core.config import settings
from src.db.db import engine
from src.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(
    title = settings.APP_NAME,
    description = 'Сервис для сокращения ссылок и перенаправления пользователей с сокращенной ссылки на внешний адрес',
    version = settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = settings.ALLOWED_METHODS,
    allow_headers = settings.ALLOWED_HEADERS,
)

app.include_router(shortener_router)
app.include_router(configuration_router)