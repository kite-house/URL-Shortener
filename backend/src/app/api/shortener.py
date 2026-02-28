from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import AfterValidator
import redis

from src.app.schemas.urls import UrlSchema
from src.app.services.generate_short_url import create_url, UrlLength
from src.app.db import crud 
from src.app.dependencies import get_session
from src.app.exceptions import URLAlreadyRegistered
from src.app.db.config import settings

router = APIRouter()
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


def checkCustomSlugValid(custom_slug: str):
    for char in custom_slug:
        if char in ['/']:
            raise ValueError(f'It is forbidden to use "{char}"!')

    for apiroute in router.routes:
        if custom_slug in apiroute.path:
            raise ValueError('This address is registered by the system!')

    return custom_slug

@router.post('/cutback', tags = ['Сut Back 🛠️'])
async def cutback(
    session: Annotated[AsyncSession, Depends(get_session)],
    long_url: UrlSchema, 
    length: Annotated[int | None, Query(ge=UrlLength.MIN_LENGTH, le=UrlLength.MAX_LENGTH)] = None, 
    custom_slug: Annotated[str | None, Query(min_length=3), AfterValidator(checkCustomSlugValid)] = None
) -> dict:
    if not custom_slug:
        slug = await create_url(session, length)

    else:
        slug = custom_slug

    try:
        await crud.write_url(
            slug = slug,
            long_url = str(long_url.url),
            session = session
        )
    except URLAlreadyRegistered:
        try:
            short_url = await crud.get_url(long_url = str(long_url.url), session = session)
        except NoResultFound:
            raise HTTPException(status_code = status.HTTP_208_ALREADY_REPORTED, detail = f'This slug has already been registered!')
        
        raise HTTPException(status_code = status.HTTP_208_ALREADY_REPORTED, detail = f'This URL is already registered in the service, using the link: {short_url.slug}')

    if redis_client:
        redis_client.set(slug, str(long_url.url))

    return {'slug' : slug, "long_url": long_url.url}

@router.get('/info/{url}', tags = ['Information 📑'])
async def info(session: Annotated[AsyncSession, Depends(get_session)], url: str) -> dict:
    try:
        url = await crud.get_url(slug = url, session = session)
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found!')
    
    return {
        'slug' : url.slug,
        'long_url' : url.long_url,
        'count_clicks' : url.count_clicks,
        'date_created' : url.date_created
    }

@router.get('/top', tags = ['Information 📑'])
async def top(session: Annotated[AsyncSession, Depends(get_session)], quantity: Annotated[int, Query(ge=1)] = 10) -> list[dict]:
    results = await crud.get_urls(session)

    results = reversed(results[:quantity])
    
    new_results = [
        {
            "id": result.id,
            "slug": result.slug,
            "long_url": result.long_url,
            "count_clicks": result.count_clicks,
            "date_created": result.date_created,
        }
        for result in results
    ]

    return new_results


@router.get('/{url}', tags = ['Redirect 🔗'])
async def redirect(session: Annotated[AsyncSession, Depends(get_session)], url: str) -> RedirectResponse:

    short_url = None

    if redis_client:
        short_url = redis_client.get(url)

    if not short_url:
        try:
            short_url = await crud.get_url(slug = url, session = session)
            short_url = short_url.long_url
        except NoResultFound:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found! Create link!')
        
    await crud.increase_count_clicks(url, session)
    return RedirectResponse(short_url, status_code = status.HTTP_302_FOUND)