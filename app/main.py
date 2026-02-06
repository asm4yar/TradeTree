"""Точка входа FastAPI-приложения."""

import logging
from contextlib import asynccontextmanager
from app.settings import BASE_DIR, settings
from app.api.router import api_router
from app.logging_config import setup_logging
from fastapi import FastAPI

# Настраиваем логирование
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App started: trade-tree")
    yield
    logger.info("App stopped: trade-tree")


def create_app() -> FastAPI:
    """Создаёт и настраивает экземпляр FastAPI.

    Returns:
        FastAPI: Инициализированное приложение с подключёнными роутерами.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )
    
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
