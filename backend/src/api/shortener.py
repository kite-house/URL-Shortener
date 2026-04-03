from fastapi import APIRouter, HTTPException, status, Query, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated
from sqlalchemy.exc import NoResultFound
from datetime import datetime

from src.schemas.urls import UrlSchema
from src.services.slug_generator import create_url
from src.services.url_checker import is_url_available
from src.db import crud 
from src.api.dependencies import SessionDep, SettingsDep, RedisDep, get_length_query, validate_custom_slug
from src.core.exceptions import URLAlreadyRegistered, SlugAlreadyRegistered
from src.services.cache import cache_url, get_cached_url
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
    custom_slug: Annotated[str | None, Depends(validate_custom_slug)] = None
) -> JSONResponse:
    long_url = url_data.original_url
    
    if not await is_url_available(long_url):
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, detail = "Данная ссылка недоступна!")

    slug = await create_url(session, settings, length) if not custom_slug else custom_slug

    try:
        await crud.write_url(slug = slug, long_url = long_url, session = session)

        if redis: background_tasks.add_task(cache_url, redis, slug, long_url, settings.REDIS_CACHE_TTL)

        return JSONResponse(
            status_code = status.HTTP_201_CREATED,
            content = {
                "success" : True,
                "cached" : redis is not None,
                "message" : "Ссылка успешно создана!",
                "data" : {
                    "slug": slug,
                    "short_url" : f"{settings.API_BASE_URL}/api/{slug}",
                    "long_url" : long_url
                }
            }
        )

    except (URLAlreadyRegistered, SlugAlreadyRegistered) as error:

        if isinstance(error, URLAlreadyRegistered):
            url = await crud.get_url(long_url = long_url, session = session)
            slug = url.slug

        elif isinstance(error, SlugAlreadyRegistered):
            url = await crud.get_url(slug = slug, session = session)
            long_url = url.long_url


        return JSONResponse(
            status_code = status.HTTP_409_CONFLICT,
            content = {
                "success" : True,
                "message" : str(error),
                "data" : {
                    "slug" : slug,
                    "short_url" : f"{settings.API_BASE_URL}/api/{slug}",
                    "long_url" : long_url
                }

            }
        )

@router.get('/info/{slug}', summary = "Получить информацию об короткой ссылке", tags = ['Information 📑'])
async def info(session: SessionDep, settings: SettingsDep, slug: str) -> JSONResponse:
    try:
        url = await crud.get_url(slug = slug, session = session)

        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {
                "success" : True,
                "message" : "Успешно найден!",
                "data" : {
                    "slug" : url.slug,
                    "short_url" : f"{settings.API_BASE_URL}/api/{url.slug}",
                    "long_url" : url.long_url,
                    "count_clicks" : url.count_clicks,
                    "date_created" : datetime.strftime(url.date_created, "%d.%m.%Y")
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
                    'date_created' : "-",
                }
            }
        )

@router.get("/top", summary = "Получить топ ссылок" ,tags = ['Information 📑'])
async def top(session: SessionDep, settings: SettingsDep, quantity: Annotated[int, Query(ge=1)] = 10) -> JSONResponse:
    results = await crud.get_urls(session)

    results = [
        {
            "id": result.id,
            "slug" : result.slug,
            "short_url": f"{settings.API_BASE_URL}/api/{result.slug}",
            "long_url": result.long_url,
            "count_clicks": result.count_clicks,
            "date_created": datetime.strftime(result.date_created, "%d.%m.%Y"),
        }
        for result in results[:quantity]
    ]

    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            "success" : True,
            "message" : f"Топ {len(results)} ссылок!",
            "data" : results
        }
    )
    
@router.get('/{slug}', summary = "Перейти по ссылке" ,tags = ['Redirect 🔗'])
async def redirect(session: SessionDep, redis: RedisDep, slug: str) -> RedirectResponse:
    short_url = None

    if redis: 
        short_url = await get_cached_url(redis, slug)

    if not short_url:
        try:
            short_url = await crud.get_url(slug = slug, session = session)
            short_url = short_url.long_url
        except NoResultFound:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Ссылка не найдена! Создайте ссылку!')
        
    await crud.increase_count_clicks(slug, session)
    return RedirectResponse(short_url, status_code = status.HTTP_302_FOUND)