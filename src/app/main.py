from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from api.shortener import router as shortener_router
from db.crud import async_main

@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_main()
    
    yield

app = FastAPI(
    title = 'Shortening-URLs',
    description= 'A service for shortening links and redirecting users from a shortened link to an external address',
    lifespan=lifespan
)

app.include_router(shortener_router)

if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)



