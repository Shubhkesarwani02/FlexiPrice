from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


# Batch Discount Schemas
class BatchDiscountBase(BaseModel):
    """Base batch discount schema."""
    batch_id: int = Field(..., gt=0, description="Inventory batch ID", alias="batchId")
    computed_price: Decimal = Field(..., gt=0, description="Computed discounted price", alias="computedPrice")
    discount_pct: Decimal = Field(..., ge=0, le=100, description="Discount percentage", alias="discountPct")
    valid_from: datetime = Field(default_factory=datetime.utcnow, description="Discount valid from", alias="validFrom")
    valid_to: Optional[datetime] = Field(None, description="Discount valid until", alias="validTo")
    ml_recommended: bool = Field(False, description="Whether discount was ML recommended", alias="mlRecommended")
    
    model_config = ConfigDict(populate_by_name=True)


class BatchDiscountCreate(BatchDiscountBase):
    """Schema for creating a new batch discount."""
    pass


class BatchDiscountUpdate(BaseModel):
    """Schema for updating an existing batch discount."""
    computed_price: Optional[Decimal] = Field(None, gt=0)
    discount_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    valid_to: Optional[datetime] = None
    ml_recommended: Optional[bool] = None


class BatchDiscountResponse(BatchDiscountBase):
    """Schema for batch discount response."""
    id: int
    created_at: datetime = Field(alias="createdAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DiscountCalculationRequest(BaseModel):
    """Schema for discount calculation request."""
    batch_id: int = Field(..., gt=0, description="Inventory batch ID")
    use_ml_recommendation: bool = Field(True, description="Use ML model for recommendation")


class DiscountCalculationResponse(BaseModel):
    """Schema for discount calculation response."""
    batch_id: int
    original_price: Decimal
    discount_pct: Decimal
    discounted_price: Decimal
    days_to_expiry: int
    ml_recommended: bool
    reason: Optional[str] = Field(None, description="Reason for discount (rule name)")
    reason: str = Field(..., description="Reason for discount percentage")
