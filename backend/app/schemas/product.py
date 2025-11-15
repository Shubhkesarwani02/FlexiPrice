from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


# Product Schemas
class ProductBase(BaseModel):
    """Base product schema."""
    sku: str = Field(..., min_length=1, max_length=100, description="Unique product SKU")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    base_price: Decimal = Field(..., gt=0, description="Base price of the product", alias="basePrice")
    
    model_config = ConfigDict(populate_by_name=True)


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    base_price: Optional[Decimal] = Field(None, gt=0)


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProductWithDiscountResponse(ProductResponse):
    """Schema for product response with current discount."""
    current_discount_pct: Optional[Decimal] = Field(None, description="Current discount percentage")
    discounted_price: Optional[Decimal] = Field(None, description="Current price after discount")
    nearest_expiry: Optional[datetime] = Field(None, description="Nearest expiry date from batches")
