from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Annotated

from src.api.dependencies import get_settings
from src.core.config import Settings

router = APIRouter(prefix="/api/config", tags = ['Configuration ⚙️'])

@router.get('/slug-length', summary = 'Получить допустимую длину для слага')
async def get_slug_length(settings: Annotated[Settings, Depends(get_settings)]) -> JSONResponse:
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            "min_slug_length": settings.MIN_SLUG_LENGTH,
            "max_slug_length": settings.MAX_SLUG_LENGTH
        }
    )
