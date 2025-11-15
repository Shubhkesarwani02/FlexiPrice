from fastapi import APIRouter
from app.api.v1.endpoints import products, inventory, discounts, ml_admin, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    products.router,
    prefix="/admin/products",
    tags=["admin-products"]
)

api_router.include_router(
    inventory.router,
    prefix="/admin/inventory",
    tags=["admin-inventory"]
)

api_router.include_router(
    discounts.router,
    prefix="/admin/discounts",
    tags=["admin-discounts"]
)

api_router.include_router(
    ml_admin.router,
    prefix="/admin/ml",
    tags=["admin-ml"]
)

api_router.include_router(
    analytics.router,
    prefix="/admin/analytics",
    tags=["admin-analytics"]
)
