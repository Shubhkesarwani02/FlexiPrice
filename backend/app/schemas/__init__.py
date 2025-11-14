from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithDiscountResponse,
)
from app.schemas.inventory import (
    InventoryBatchBase,
    InventoryBatchCreate,
    InventoryBatchUpdate,
    InventoryBatchResponse,
    InventoryBatchWithProductResponse,
)
from app.schemas.discount import (
    BatchDiscountBase,
    BatchDiscountCreate,
    BatchDiscountUpdate,
    BatchDiscountResponse,
    DiscountCalculationRequest,
    DiscountCalculationResponse,
)
from app.schemas.order import (
    OrderStatusEnum,
    OrderItemBase,
    OrderItemCreate,
    OrderItemResponse,
    OrderBase,
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderWithItemsResponse,
)
from app.schemas.price_history import (
    PriceHistoryBase,
    PriceHistoryCreate,
    PriceHistoryResponse,
)

__all__ = [
    # Product
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductWithDiscountResponse",
    # Inventory
    "InventoryBatchBase",
    "InventoryBatchCreate",
    "InventoryBatchUpdate",
    "InventoryBatchResponse",
    "InventoryBatchWithProductResponse",
    # Discount
    "BatchDiscountBase",
    "BatchDiscountCreate",
    "BatchDiscountUpdate",
    "BatchDiscountResponse",
    "DiscountCalculationRequest",
    "DiscountCalculationResponse",
    # Order
    "OrderStatusEnum",
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderWithItemsResponse",
    # Price History
    "PriceHistoryBase",
    "PriceHistoryCreate",
    "PriceHistoryResponse",
]
