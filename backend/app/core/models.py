from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with Base
from app.models.product import Product
from app.models.inventory import InventoryBatch
from app.models.discount import BatchDiscount
from app.models.order import Order, OrderItem
from app.models.price_history import PriceHistory

__all__ = [
    "Base",
    "Product",
    "InventoryBatch",
    "BatchDiscount",
    "Order",
    "OrderItem",
    "PriceHistory",
]
