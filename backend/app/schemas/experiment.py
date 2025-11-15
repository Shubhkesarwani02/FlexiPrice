"""A/B Testing schemas for experiment management."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class ExperimentGroup(str, Enum):
    """Experiment group assignment."""
    CONTROL = "CONTROL"  # Rule-based discounts
    ML_VARIANT = "ML_VARIANT"  # ML-recommended discounts


class ExperimentAssignment(BaseModel):
    """Product experiment group assignment."""
    product_id: int = Field(..., alias="productId")
    sku: str
    experiment_group: ExperimentGroup = Field(..., alias="experimentGroup")
    assigned_at: Optional[datetime] = Field(None, alias="assignedAt")
    
    class Config:
        populate_by_name = True


class ExperimentAssignRequest(BaseModel):
    """Request to assign products to experiment groups."""
    product_ids: List[int] = Field(..., alias="productIds", min_items=1)
    experiment_group: ExperimentGroup = Field(..., alias="experimentGroup")
    
    class Config:
        populate_by_name = True


class ExperimentMetric(BaseModel):
    """Metrics for a product in an experiment."""
    id: int
    product_id: int = Field(..., alias="productId")
    experiment_group: ExperimentGroup = Field(..., alias="experimentGroup")
    impressions: int = 0
    conversions: int = 0
    revenue: Decimal = Decimal("0.00")
    units_sold: int = Field(0, alias="unitsSold")
    avg_discount_pct: Optional[Decimal] = Field(None, alias="avgDiscountPct")
    conversion_rate: Optional[Decimal] = Field(None, alias="conversionRate")  # Computed
    period_start: datetime = Field(..., alias="periodStart")
    period_end: datetime = Field(..., alias="periodEnd")
    
    class Config:
        populate_by_name = True


class ExperimentSummary(BaseModel):
    """Summary of experiment performance by group."""
    experiment_group: ExperimentGroup = Field(..., alias="experimentGroup")
    total_products: int = Field(..., alias="totalProducts")
    total_impressions: int = Field(..., alias="totalImpressions")
    total_conversions: int = Field(..., alias="totalConversions")
    total_revenue: Decimal = Field(..., alias="totalRevenue")
    total_units_sold: int = Field(..., alias="totalUnitsSold")
    avg_discount_pct: Decimal = Field(..., alias="avgDiscountPct")
    conversion_rate: Decimal = Field(..., alias="conversionRate")
    revenue_per_product: Decimal = Field(..., alias="revenuePerProduct")
    
    class Config:
        populate_by_name = True


class ExperimentComparison(BaseModel):
    """A/B test comparison results."""
    control: ExperimentSummary
    ml_variant: ExperimentSummary
    
    # Relative improvements (ML vs Control)
    conversion_lift: Decimal = Field(..., alias="conversionLift", description="% improvement in conversion rate")
    revenue_lift: Decimal = Field(..., alias="revenueLift", description="% improvement in revenue per product")
    units_lift: Decimal = Field(..., alias="unitsLift", description="% improvement in units sold")
    
    period_start: datetime = Field(..., alias="periodStart")
    period_end: datetime = Field(..., alias="periodEnd")
    
    class Config:
        populate_by_name = True


class RecommendationRequest(BaseModel):
    """Request for discount recommendation (respects experiment group)."""
    product_id: int = Field(..., alias="productId")
    days_to_expiry: int = Field(..., ge=1, alias="daysToExpiry")
    inventory: int = Field(..., ge=1)
    top_k: int = Field(default=3, ge=1, le=10, alias="topK")
    
    class Config:
        populate_by_name = True


class RecommendationResponse(BaseModel):
    """Discount recommendation response."""
    product_id: int = Field(..., alias="productId")
    experiment_group: ExperimentGroup = Field(..., alias="experimentGroup")
    recommended_discount_pct: Decimal = Field(..., alias="recommendedDiscountPct")
    expected_probability: Optional[Decimal] = Field(None, alias="expectedProbability")
    method: str = Field(..., description="'ml' or 'rule_based'")
    reason: str
    
    class Config:
        populate_by_name = True


class ProductWithExperiment(BaseModel):
    """Product with experiment assignment."""
    id: int
    sku: str
    name: str
    category: Optional[str]
    base_price: Decimal = Field(..., alias="basePrice")
    experiment_group: Optional[ExperimentGroup] = Field(None, alias="experimentGroup")
    experiment_assigned_at: Optional[datetime] = Field(None, alias="experimentAssignedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True
