from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from src.core.config import settings
from src.core.logging import logger
from src.api.shortener import router as shortener_router
from src.api.configuration import router as configuration_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_dir = Path("/app/logs")
    if log_dir.exists():
        logger.info(f"📄 Файлы логов: {list(log_dir.glob('*.log'))}")
    
    yield

app = FastAPI(
    title = settings.APP_NAME,
    description = 'Сервис для сокращения ссылок и перенаправления пользователей с сокращенной ссылки на внешний адрес',
    version = settings.VERSION,
    lifespan = lifespan
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