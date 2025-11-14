from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


# Price History Schemas
class PriceHistoryBase(BaseModel):
    """Base price history schema."""
    product_id: int = Field(..., gt=0, description="Product ID")
    price: Decimal = Field(..., gt=0, description="Price at this point")
    discount_pct: Decimal = Field(0.0, ge=0, le=100, description="Discount percentage")
    reason: Optional[str] = Field(None, max_length=100, description="Reason for price change")


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating a price history entry."""
    pass


class PriceHistoryResponse(PriceHistoryBase):
    """Schema for price history response."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
