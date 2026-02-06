from app.settings import settings
from app.api.endpoints import router as api_router
from fastapi import FastAPI


def create_app() -> FastAPI:

    app = FastAPI(title=settings.app_name, version=settings.version)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
