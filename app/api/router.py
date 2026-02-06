from fastapi import APIRouter
from app.api.catalog import routers as catalog_routers

api_router = APIRouter()

for router in catalog_routers:
    api_router.include_router(router=router)
