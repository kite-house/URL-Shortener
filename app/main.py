from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
import uvicorn
import asyncio

from src.schemas import UrlSchema
from src.url import create_url
from db import crud 

app = FastAPI(
    title = 'Shortening-URLs',
    description= 'A service for shortening links and redirecting users from a shortened link to an external address'
)


@app.post('/cutback')
async def cutback(url: UrlSchema):
    new_url = await create_url()
    try:
        await crud.write_url(
            abbreviated_link = new_url,
            address = url.url
        )
    except IntegrityError:
        new_url = await crud.get_url_reverse(url.url)
        raise HTTPException(status_code=208, detail = f'This URL is already registered in the service, using the link: {new_url}')

    return {'url' : new_url}

@app.get('/{url}')
async def redirect(url: str):
    try:
        address = await crud.get_url(url)
    except ValueError:
        raise HTTPException(status_code=404, detail='Link not found! Create link!')
    
    await crud.translation_count(url)
    return RedirectResponse(address)


if __name__ == "__main__":
    asyncio.run(crud.async_main())
    uvicorn.run('main:app', reload=True)



