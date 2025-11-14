from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


# Inventory Batch Schemas
class InventoryBatchBase(BaseModel):
    """Base inventory batch schema."""
    product_id: int = Field(..., gt=0, description="Product ID")
    batch_code: Optional[str] = Field(None, max_length=100, description="Batch identification code")
    quantity: int = Field(..., gt=0, description="Quantity in this batch")
    expiry_date: date = Field(..., description="Expiry date of this batch")


class InventoryBatchCreate(InventoryBatchBase):
    """Schema for creating a new inventory batch."""
    pass


class InventoryBatchUpdate(BaseModel):
    """Schema for updating an existing inventory batch."""
    batch_code: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    expiry_date: Optional[date] = None


class InventoryBatchResponse(InventoryBatchBase):
    """Schema for inventory batch response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class InventoryBatchWithProductResponse(InventoryBatchResponse):
    """Schema for inventory batch response with product details."""
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    days_to_expiry: Optional[int] = Field(None, description="Days until expiry")
    current_discount_pct: Optional[Decimal] = Field(None, description="Current discount for this batch")
