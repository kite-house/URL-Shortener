from fastapi import FastAPI
import uvicorn

from api.shortening import router as shortening_router
from lifespan import lifespan

app = FastAPI(
    title = 'Shortening-URLs',
    description= 'A service for shortening links and redirecting users from a shortened link to an external address',
    lifespan=lifespan
)

app.include_router(shortening_router)

if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)



