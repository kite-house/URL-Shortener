from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_easylimiter import RateLimitMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio

from src.core.config import settings
from src.core.logging import logger
from src.core.redis import RedisService
from src.api.shortener import router as shortener_router
from src.api.configuration import router as configuration_router
from src.db.db import async_session
from src.db.crud import increment_count_clicks

async def analytics_flusher(redis: RedisService):
    while True:
        await asyncio.sleep(settings.ANALYTICS_FLUSH_INTERVAL)

        try:
            cursor = 0
            processed = 0
            
            async with async_session() as session:
                while True:
                    cursor, batch = await redis.hscan("counter_transmissions", cursor, count=100)
                    
                    for key, value in batch.items():
                        await increment_count_clicks(session, key, int(value))
                        processed += 1
                    
                    if processed > 0:
                        await session.commit()
                    
                    if cursor == 0:
                        break
            
            if processed > 0:
                await redis.delete("counter_transmissions")
            
        except Exception as error:
            logger.error(str(error))

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_dir = Path("/app/logs")
    if log_dir.exists():
        logger.info(f"📄 Файлы логов: {list(log_dir.glob('*.log'))}")

    if hasattr(app.state, 'rate_limit_redis'):
        if await app.state.rate_limit_redis.ping():
            logger.info("✅ Redis подключен для rate limiting")
        else:
            logger.error("❌ Не удалось подключиться к Redis!")

    analytics_redis = RedisService(settings)
    analytics_flusher_task = asyncio.create_task(analytics_flusher(analytics_redis))

    
    yield

    analytics_flusher_task.cancel()

app = FastAPI(
    title=settings.APP_NAME,
    description='Сервис для сокращения ссылок и перенаправления пользователей с сокращенной ссылки на внешний адрес',
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

if settings.RATE_LIMIT_ENABLED and settings.MODE != "TEST":
    from fastapi_easylimiter import RateLimitMiddleware
    from src.core.redis import RedisService

    redis_service = RedisService(settings, db=settings.RATE_LIMIT_REDIS_DB)
    app.state.rate_limit_redis = redis_service
    
    app.add_middleware(
        RateLimitMiddleware,
        redis=redis_service.client,
        rules=settings.RATE_LIMIT_RULES,  
        ban_offenses=settings.RATE_LIMIT_BAN_OFFENSES,
        ban_length=settings.RATE_LIMIT_BAN_LENGTH,
        site_ban=settings.RATE_LIMIT_SITE_BAN,
    )
    
    rules = settings.RATE_LIMIT_RULES
    logger.info(
        f"🛡️ Rate limiting активирован\n"
        f"INFO:     📌 Правила:\n"
        f"INFO:       • Создание ссылки → {rules['/api/shorten'][0]} в минуту\n"
        f"INFO:       • Получение инфо → {rules['/api/info/*'][0]} в минуту\n"
        f"INFO:       • Редирект → {rules['/{slug}'][0]} в минуту\n"
        f"INFO:       • Глобально → {rules['/*'][0]} в час\n"
        f"INFO:     ⚠️  Автобан: после {settings.RATE_LIMIT_BAN_OFFENSES} превышений на {settings.RATE_LIMIT_BAN_LENGTH}"
    )
else:
    logger.info("🔓 Rate limiting отключён")


app.include_router(shortener_router)
app.include_router(configuration_router)