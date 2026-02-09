from fastapi import FastAPI, Depends
from typing import Annotated
from functools import lru_cache
import logging

from src import config
from src.health import router as health_router
from src.middleware import RequestIdMiddleware
from src.logging import setup_logging


@lru_cache
def get_settings():
    return config.Settings()

def create_app() -> FastAPI:
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting application")

    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )

    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)

    @app.on_event("shutdown")
    def shutdown_event():
        logger.info("Shutting down application")

    return app

app = create_app()
