"""Analytics schemas for dashboard visualizations."""

from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class SalesVsExpiryDataPoint(BaseModel):
    """Data point for sales vs expiry chart."""
    days_to_expiry: int = Field(..., description="Days until expiry", alias="daysToExpiry")
    total_units_sold: int = Field(..., description="Total units sold", alias="totalUnitsSold")
    total_revenue: Decimal = Field(..., description="Total revenue generated", alias="totalRevenue")
    avg_discount_pct: Optional[Decimal] = Field(None, description="Average discount percentage", alias="avgDiscountPct")
    product_count: int = Field(..., description="Number of products in this bucket", alias="productCount")
    
    class Config:
        populate_by_name = True


class DiscountVsUnitsDataPoint(BaseModel):
    """Data point for discount vs units sold chart."""
    discount_range: str = Field(..., description="Discount range (e.g., '10-20%')", alias="discountRange")
    discount_avg: Decimal = Field(..., description="Average discount in range", alias="discountAvg")
    total_units_sold: int = Field(..., description="Total units sold", alias="totalUnitsSold")
    total_revenue: Decimal = Field(..., description="Total revenue", alias="totalRevenue")
    transaction_count: int = Field(..., description="Number of transactions", alias="transactionCount")
    conversion_rate: Optional[Decimal] = Field(None, description="Conversion rate", alias="conversionRate")
    
    class Config:
        populate_by_name = True


class CategoryPerformance(BaseModel):
    """Category-level performance metrics."""
    category: str = Field(..., description="Product category")
    total_units_sold: int = Field(..., alias="totalUnitsSold")
    total_revenue: Decimal = Field(..., alias="totalRevenue")
    avg_discount_pct: Decimal = Field(..., alias="avgDiscountPct")
    
    class Config:
        populate_by_name = True


class AnalyticsSummary(BaseModel):
    """Overall analytics summary."""
    total_revenue: Decimal = Field(..., description="Total revenue", alias="totalRevenue")
    total_units_sold: int = Field(..., description="Total units sold", alias="totalUnitsSold")
    avg_discount_pct: Decimal = Field(..., description="Average discount", alias="avgDiscountPct")
    products_with_discount: int = Field(..., description="Products with active discount", alias="productsWithDiscount")
    products_expiring_soon: int = Field(..., description="Products expiring within 7 days", alias="productsExpiringSoon")
    
    class Config:
        populate_by_name = True


class AnalyticsDashboardResponse(BaseModel):
    """Complete analytics dashboard response."""
    summary: AnalyticsSummary
    sales_vs_expiry: List[SalesVsExpiryDataPoint] = Field(..., alias="salesVsExpiry")
    discount_vs_units: List[DiscountVsUnitsDataPoint] = Field(..., alias="discountVsUnits")
    category_performance: List[CategoryPerformance] = Field(..., alias="categoryPerformance")
    
    class Config:
        populate_by_name = True
