from fastapi import FastAPI, Depends
from typing import Annotated
from functools import lru_cache

from . import config
from .health import router as health_router


@lru_cache
def get_settings():
    return config.Settings()

app = FastAPI(title=get_settings().APP_NAME)

@app.get("/info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.APP_NAME,
        "env": settings.ENV,
        "debug": settings.DEBUG
    }


app.include_router(health_router)