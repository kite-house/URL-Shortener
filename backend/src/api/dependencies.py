from fastapi import Depends, Request, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated

from src.db.db import async_session
from src.core.config import Settings
from src.core.redis import RedisService
from src.services.validators import SlugValidator
from src.core.logging import logger

# ==========================  Settings  ===================================
async def get_settings() -> AsyncGenerator[Settings, None]:
    settings = Settings()
    yield settings

SettingsDep = Annotated[Settings, Depends(get_settings)] 

# ===========================  Session  ====================================
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as error:
            logger.error(str(error))
            await session.rollback()
            raise
        finally:
            await session.close()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# ========================  REDIS_SERVICE  =================================
async def get_redis_service(settings: SettingsDep) -> AsyncGenerator[RedisService, None]:
    redis_service = RedisService(settings)
    try:
        await redis_service.client.ping()
        yield redis_service
    finally:
        await redis_service.close()

RedisDep = Annotated[RedisService, Depends(get_redis_service)]



# ============================ Validation =================================

async def get_length_query(
    settings: SettingsDep,
    length: int | None = Query(None, description="Длина генерируемого слага")
) -> int | None:
    """Dependency: валидация параметра длины"""
    if length is not None:
        if length < settings.SLUG_MIN_LENGTH or length > settings.SLUG_MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Length must be between {settings.SLUG_MIN_LENGTH} and {settings.SLUG_MAX_LENGTH}"
            )
    return length


async def validate_custom_slug(
    request: Request,
    settings: SettingsDep,
    custom_slug: str | None = Query(None, min_length=3, description="Custom slug")
) -> str | None:
    """Dependency: полная валидация кастомного слага"""
    if not custom_slug:
        return None
    
    try:
        SlugValidator.validate_characters(custom_slug)
        
        SlugValidator.validate_length(custom_slug, settings)
        
        system_routes = {route.path for route in request.app.routes 
                        if not getattr(route, 'include_in_schema', True)}
        SlugValidator.validate_system_routes(custom_slug, system_routes)
        
        return custom_slug
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )