# backend/src/main.py
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import logging

from src.db import create_db_and_tables
from src.health import router as health_router
from src.auth.router import router as auth_router
from src.middleware import RequestIdMiddleware
from src.logging import setup_logging
from src.config import get_settings
from src.db import create_db_and_tables



def create_app() -> FastAPI:
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting application")

    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )

    # now managed by Alembic migrations
    # @app.on_event("startup")
    # def on_startup():
    #     create_db_and_tables()

    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)
    app.include_router(auth_router)

    @app.on_event("shutdown")
    def shutdown_event():
        logger.info("Shutting down application")

    return app

app = create_app()