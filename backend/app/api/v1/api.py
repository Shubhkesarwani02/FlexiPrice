from fastapi import APIRouter
from app.api.v1.endpoints import products, inventory, discounts, storefront

api_router = APIRouter()

# Admin endpoints
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
    prefix="/discounts",
    tags=["discounts"]
)

# Public/Storefront endpoints
api_router.include_router(
    storefront.router,
    prefix="/storefront",
    tags=["storefront"]
)
