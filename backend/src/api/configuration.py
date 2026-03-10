from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Annotated

from src.schemas.urls import UrlSchema
from src.api.dependencies import SettingsDep

router = APIRouter(prefix="/api/config", tags = ['Configuration ⚙️'])

@router.get('/slug-length', summary = 'Получить допустимую длину для слага')
async def get_slug_length(settings: SettingsDep) -> JSONResponse:
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            "slug_min_length": settings.SLUG_MIN_LENGTH,
            "slug_max_length": settings.SLUG_MAX_LENGTH
        }
    )

@router.get("/frontend", summary = "Получить всю необходимую информацию о сервере")
async def get_frontend_config(settings: SettingsDep) -> JSONResponse:
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = {
            "app_name": settings.APP_NAME,
            "version": settings.VERSION,
            "api_base_url": settings.API_BASE_URL,
            "mode": settings.MODE,
            "example_url": UrlSchema.Config.json_schema_extra["example"]["url"]
        }
    )