from fastapi import FastAPI
from contextlib import asynccontextmanager

from db.crud import async_main

@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_main()
    
    yield