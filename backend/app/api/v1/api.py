from fastapi import APIRouter
from app.api.v1.endpoints import products, inventory

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
