from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Annotated
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import AfterValidator
from redis import Redis
from datetime import datetime

from src.schemas.urls import UrlSchema
from src.services.slug_generator import create_url
from src.db import crud 
from src.api.dependencies import get_session, get_settings
from src.core.exceptions import URLAlreadyRegistered
from src.core.config import settings, Settings

router = APIRouter(prefix = '/api')
redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


def checkCustomSlugValid(custom_slug: str):
    for char in custom_slug:
        if char in ['/', '?', '@', "#"]:
            raise ValueError(f'It is forbidden to use "{char}"!')

    for apiroute in router.routes:
        if custom_slug in apiroute.path:
            raise ValueError('This address is registered by the system!')

    return custom_slug

@router.post('/shorten', summary = "Сократить ссылку", tags = ['Shorten 🛠️'])
async def shorten(session: Annotated[AsyncSession, Depends(get_session)], long_url: UrlSchema, 
                  length: Annotated[int | None, Query(ge=settings.MIN_SLUG_LENGTH, le=settings.MAX_SLUG_LENGTH)] = None,  
                  custom_slug: Annotated[str | None, Query(min_length=3), AfterValidator(checkCustomSlugValid)] = None) -> JSONResponse:

    slug = await create_url(session, length) if not custom_slug else custom_slug

    try:
        await crud.write_url(slug = slug, long_url = str(long_url.url), session = session)
    except URLAlreadyRegistered:
        try:
            await crud.get_url(long_url = str(long_url.url), session = session)
        except NoResultFound:
            return JSONResponse(
                status_code = status.HTTP_208_ALREADY_REPORTED,
                content = {
                    "success" : True,
                    "message" : "Короткая ссылка уже зарегистрирована в сервисе!",
                    "data" : {
                        "slug" : slug,
                        "short_url" : f"{settings.BASE_URL}/api/{slug}",
                        "long_url" : str(long_url.url)
                    }

                }
            )
        
        return JSONResponse(
            status_code = status.HTTP_208_ALREADY_REPORTED,
            content = {
                "success" : True,
                "message" : "Ссылка уже зарегистрирована в сервисе!",
                "data" : {
                    "slug" : slug,
                    "short_url" : f"{settings.BASE_URL}/api/{slug}",
                    "long_url" : str(long_url.url)
                }

            }
        )

    if redis_client: redis_client.set(slug, str(long_url.url))
    
    return JSONResponse(
        status_code = status.HTTP_201_CREATED,
        content = {
            "success" : True,
            "message" : "Ссылка успешно создана!",
            "data" : {
                "slug": slug,
                "short_url" : f"{settings.BASE_URL}/api/{slug}",
                "long_url" : str(long_url.url)
            }
        }
    )

@router.get('/info/{slug}', summary = "Получить информацию об короткой ссылке", tags = ['Information 📑'])
async def info(session: Annotated[AsyncSession, Depends(get_session)], slug: str) -> JSONResponse:
    try:
        url = await crud.get_url(slug = slug, session = session)
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
    
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            "success" : True,
            "message" : "Успешно найден!",
            "data" : {
                "slug" : url.slug,
                "short_url" : f"{settings.BASE_URL}/api/{url.slug}",
                "long_url" : url.long_url,
                "count_clicks" : url.count_clicks,
                "date_created" : datetime.strftime(url.date_created, "%d.%m.%Y")
            } 
        }
    )

@router.get("/top", summary = "Получить топ ссылок" ,tags = ['Information 📑'])
async def top(session: Annotated[AsyncSession, Depends(get_session)], quantity: Annotated[int, Query(ge=1)] = 10) -> JSONResponse:
    results = await crud.get_urls(session)

    results = [
        {
            "id": result.id,
            "slug" : result.slug,
            "short_url": f"{settings.BASE_URL}/api/{result.slug}",
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
async def redirect(session: Annotated[AsyncSession, Depends(get_session)], slug: str) -> RedirectResponse:
    short_url = None

    if redis_client:
        short_url = redis_client.get(slug)

    if not short_url:
        try:
            short_url = await crud.get_url(slug = slug, session = session)
            short_url = short_url.long_url
        except NoResultFound:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found! Create link!')
        
    await crud.increase_count_clicks(slug, session)
    return RedirectResponse(short_url, status_code = status.HTTP_302_FOUND)