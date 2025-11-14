from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum


# Order Status Enum
class OrderStatusEnum(str, Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# Order Item Schemas
class OrderItemBase(BaseModel):
    """Base order item schema."""
    product_id: int = Field(..., gt=0, description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., gt=0, description="Unit price at time of order")
    discount_pct: Decimal = Field(0.0, ge=0, le=100, description="Discount percentage applied")
    total_price: Decimal = Field(..., gt=0, description="Total price for this item")


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderItemResponse(OrderItemBase):
    """Schema for order item response."""
    id: int
    order_id: int
    
    model_config = ConfigDict(from_attributes=True)


# Order Schemas
class OrderBase(BaseModel):
    """Base order schema."""
    customer_email: Optional[str] = Field(None, description="Customer email address")


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Order items")


class OrderUpdate(BaseModel):
    """Schema for updating an existing order."""
    status: Optional[OrderStatusEnum] = None
    customer_email: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order response."""
    id: int
    order_number: str
    total_amount: Decimal
    status: OrderStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderWithItemsResponse(OrderResponse):
    """Schema for order response with items."""
    items: List[OrderItemResponse] = []
