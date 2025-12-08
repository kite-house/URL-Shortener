from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

from schemas.urls import UrlSchema
from services.generate_short_url import create_url
from db import crud 

router = APIRouter()

@router.post('/cutback', tags = ['Сut Back 🛠️'])
async def cutback(long_url: UrlSchema):
    short_url = await create_url()
    try:
        await crud.write_url(
            slug = short_url,
            long_url = long_url.url
        )
    except IntegrityError:
        short_url = await crud.get_url(long_url = long_url.url)
        raise HTTPException(status_code = status.HTTP_208_ALREADY_REPORTED, detail = f'This URL is already registered in the service, using the link: {short_url.slug}')

    return {'short_url' : short_url.slug, "long_url": long_url.url}

@router.get('/{url}', tags = ['Redirect 🔗'])
async def redirect(url: str):
    try:
        short_url = await crud.get_url(slug = url)
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found! Create link!')
    
    await crud.increase_count_clicks(url)
    return RedirectResponse(short_url.long_url, status_code = status.HTTP_302_FOUND)

@router.get('/info/{url}', tags = ['Information 📑'])
async def info(url: str):
    try:
        url = await crud.get_url(slug = url)
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Link not found!')
    
    return {
        'slug' : url.slug,
        'long_url' : url.long_url,
        'number_clicks' : url.number_clicks,
        'date_created' : url.date_created
    }