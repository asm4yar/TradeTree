from .orders import router as order_router
from .categories import router as categories_router

routers = (order_router, categories_router)

__ALL__ = ["routers"]
