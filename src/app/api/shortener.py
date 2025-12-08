from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.exc import IntegrityError, NoResultFound

from schemas.urls import UrlSchema
from services.generate_short_url import create_url, UrlLength
from db import crud 

router = APIRouter()

@router.post('/cutback', tags = ['Сut Back 🛠️'])
async def cutback(long_url: UrlSchema, length: Annotated[int | None, Query(ge=UrlLength.MIN_LENGTH, le=UrlLength.MAX_LENGTH)] = None) -> dict:
    short_url = await create_url(length)
    try:
        await crud.write_url(
            slug = short_url,
            long_url = long_url.url
        )
    except IntegrityError:
        short_url = await crud.get_url(long_url = long_url.url)
        raise HTTPException(status_code = status.HTTP_208_ALREADY_REPORTED, detail = f'This URL is already registered in the service, using the link: {short_url.slug}')

    return {'short_url' : short_url, "long_url": long_url.url}

@router.get('/info/{url}', tags = ['Information 📑'])
async def info(url: str) -> dict:
    try:
        url = await crud.get_url(slug = url)
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found!')
    
    return {
        'slug' : url.slug,
        'long_url' : url.long_url,
        'count_clicks' : url.count_clicks,
        'date_created' : url.date_created
    }

@router.get('/top', tags = ['Information 📑'])
async def top(quantity: Annotated[int, Query(ge=1)] = 10) -> list[dict]:
    results = await crud.get_urls()

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
async def redirect(url: str) -> RedirectResponse:
    try:
        short_url = await crud.get_url(slug = url)
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found! Create link!')
    
    await crud.increase_count_clicks(url)
    return RedirectResponse(short_url.long_url, status_code = status.HTTP_302_FOUND)