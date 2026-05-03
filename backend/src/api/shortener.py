from fastapi import APIRouter, HTTPException, status, Query, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated, Optional
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta, timezone

from src.schemas.urls import UrlSchema
from src.services.slug_generator import create_url
from src.services.url_checker import is_url_available
from src.db import crud 
from src.api.dependencies import SessionDep, SettingsDep, RedisDep, get_length_query, validate_custom_slug
from src.core.exceptions import URLAlreadyRegistered, SlugAlreadyRegistered
from src.services.cache import cache_url, get_cached_url, increment_click_counter, reset_click_counter
from src.core.logging import logger

router = APIRouter(prefix = '/api')


@router.post('/shorten')
async def shorten(
    session: SessionDep,
    url_data: UrlSchema,
    settings: SettingsDep,
    redis: RedisDep,
    background_tasks: BackgroundTasks,
    length: Annotated[int | None, Depends(get_length_query)] = None,
    custom_slug: Annotated[str | None, Depends(validate_custom_slug)] = None,
    ttl_days: Annotated[Optional[int], Query(ge=1, le=365, description="TTL в днях")] = None
) -> JSONResponse:
    long_url = url_data.original_url

    if not await is_url_available(long_url):
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, detail = "Данная ссылка недоступна!")

    slug = custom_slug or await create_url(session, settings, length)
    ttl_expiry = datetime.now(timezone.utc) + timedelta(days = ttl_days) if ttl_days else None

    try:
        db_url = await crud.write_url(session, slug, long_url, ttl_expiry)

        background_tasks.add_task(cache_url, redis, slug, long_url, db_url.ttl, settings.REDIS_CACHE_TTL)

        return JSONResponse(
            status_code = status.HTTP_201_CREATED,
            content = {
                "success" : True,
                "cached" : redis is not None,
                "message" : "Ссылка успешно создана!",
                "data" : {
                    "slug": db_url.slug,
                    "short_url" : f"{settings.API_BASE_URL}/api/{db_url.slug}",
                    "long_url" : db_url.long_url,
                    "is_active": db_url.is_active,
                    "ttl" : db_url.ttl.isoformat() if db_url.ttl else None,
                    "date_created" : db_url.date_created.isoformat()
                }
            }
        )

    except (URLAlreadyRegistered, SlugAlreadyRegistered) as error:
        if isinstance(error, URLAlreadyRegistered):
            existing_url = await crud.get_url(session, long_url = long_url)

        elif isinstance(error, SlugAlreadyRegistered):
            existing_url = await crud.get_url(session, slug = slug)

        background_tasks.add_task(cache_url, redis, slug, existing_url.long_url, existing_url.ttl, settings.REDIS_CACHE_TTL)

        return JSONResponse(
            status_code = status.HTTP_409_CONFLICT,
            content = {
                "success" : True,
                "cached" : redis is not None,
                "message" : str(error),
                "data" : {
                    "slug" : existing_url.slug,
                    "short_url" : f"{settings.API_BASE_URL}/api/{existing_url.slug}",
                    "long_url" : existing_url.long_url,
                    "is_active": existing_url.is_active,
                    "ttl" : existing_url.ttl.isoformat() if existing_url.ttl else None,
                    "date_created" : existing_url.date_created.isoformat()
                }

            }
        )

    except Exception as error:
        logger.error(str(error))
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже.")

@router.get('/info/{slug}', summary = "Получить информацию об короткой ссылке", tags = ['Information 📑'])
async def info(session: SessionDep, settings: SettingsDep, slug: str) -> JSONResponse:
    try:
        db_url = await crud.get_url(session, slug)

        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {
                "success" : True,
                "message" : "Успешно найден!",
                "data" : {
                    "slug" : db_url.slug,
                    "short_url" : f"{settings.API_BASE_URL}/api/{db_url.slug}",
                    "long_url" : db_url.long_url,
                    "count_clicks" : db_url.count_clicks,
                    "is_active" : db_url.is_active,
                    "ttl": db_url.ttl.isoformat() if db_url.ttl else None,
                    "date_created" : db_url.date_created.isoformat()
                } 
            }
        )
    
    except NoResultFound:
        return JSONResponse(
            status_code = status.HTTP_404_NOT_FOUND,
            content = {
                "success" : True,
                "message" : "Не удалось найти!",
                "data" : {
                    'slug' : slug,
                    "short_url" : "-",
                    'long_url' : "-",
                    'count_clicks' : "-",
                    'is_active' : False,
                    'ttl': "-",
                    'date_created' : "-",
                }
            }
        )
    
    except Exception as error:
        logger.error(str(error))
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже.")
    
@router.get('/{slug}', summary = "Перейти по ссылке" ,tags = ['Redirect 🔗'])
async def redirect(session: SessionDep, settings: SettingsDep, redis: RedisDep, background_tasks: BackgroundTasks,slug: str) -> RedirectResponse:
    long_url, is_active = await get_cached_url(redis, slug)

    if not is_active or not long_url:
        try:
            db_url = await crud.get_url(session, slug)
            if not db_url.update_is_active():
                raise HTTPException(status_code = status.HTTP_410_GONE, detail = "Срок действия ссылки истек!")
            long_url = db_url.long_url
            background_tasks.add_task(cache_url, redis, slug, long_url, db_url.ttl, settings.REDIS_CACHE_TTL)
        except NoResultFound:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Ссылка не найдена!')
    
    await increment_click_counter(redis, slug)
    return RedirectResponse(long_url, status_code = status.HTTP_302_FOUND)