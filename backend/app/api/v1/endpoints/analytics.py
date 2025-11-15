"""
Analytics API endpoints for dashboard visualizations.

Provides data for:
- Sales vs Expiry charts
- Discount vs Units Sold charts
- Category performance metrics
- Summary statistics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from decimal import Decimal
import pandas as pd
from pathlib import Path

from app.schemas.analytics import (
    AnalyticsDashboardResponse,
    AnalyticsSummary,
    SalesVsExpiryDataPoint,
    DiscountVsUnitsDataPoint,
    CategoryPerformance,
)

router = APIRouter()


def load_synthetic_data() -> pd.DataFrame:
    """Load synthetic purchase data for analytics."""
    data_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "synthetic_purchases.csv"
    
    if not data_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Synthetic data not found at {data_path}. Run generate_synthetic_data.py first."
        )
    
    try:
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load synthetic data: {str(e)}"
        )


def aggregate_sales_vs_expiry(df: pd.DataFrame) -> List[SalesVsExpiryDataPoint]:
    """Aggregate sales data by days to expiry."""
    # Filter to sold items only
    sold_df = df[df['sold'] == 1].copy()
    
    if sold_df.empty:
        return []
    
    # Group by days_to_expiry
    grouped = sold_df.groupby('days_to_expiry').agg({
        'units_sold': 'sum',
        'base_price': 'sum',  # Revenue proxy (would be actual revenue in production)
        'discount_pct': 'mean',
        'product_id': 'count'
    }).reset_index()
    
    # Calculate revenue (base_price * (1 - discount_pct/100) * units_sold)
    # For simplicity, using total base_price as proxy
    grouped['revenue'] = grouped['base_price'] * (1 - grouped['discount_pct'] / 100)
    
    # Sort by days_to_expiry
    grouped = grouped.sort_values('days_to_expiry')
    
    # Convert to schema
    result = []
    for _, row in grouped.iterrows():
        result.append(SalesVsExpiryDataPoint(
            days_to_expiry=int(row['days_to_expiry']),
            total_units_sold=int(row['units_sold']),
            total_revenue=Decimal(str(round(row['revenue'], 2))),
            avg_discount_pct=Decimal(str(round(row['discount_pct'], 2))),
            product_count=int(row['product_id'])
        ))
    
    return result


def aggregate_discount_vs_units(df: pd.DataFrame) -> List[DiscountVsUnitsDataPoint]:
    """Aggregate units sold by discount ranges."""
    sold_df = df[df['sold'] == 1].copy()
    
    if sold_df.empty:
        return []
    
    # Create discount buckets
    bins = [0, 10, 20, 30, 40, 50, 100]
    labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+']
    sold_df['discount_bucket'] = pd.cut(sold_df['discount_pct'], bins=bins, labels=labels, include_lowest=True)
    
    # Group by discount bucket
    grouped = sold_df.groupby('discount_bucket', observed=True).agg({
        'units_sold': 'sum',
        'discount_pct': 'mean',
        'base_price': 'sum',
        'product_id': 'count'
    }).reset_index()
    
    # Calculate revenue
    grouped['revenue'] = grouped['base_price'] * (1 - grouped['discount_pct'] / 100)
    
    # Calculate conversion rate (sold / total in that discount range)
    total_by_bucket = df.groupby(
        pd.cut(df['discount_pct'], bins=bins, labels=labels, include_lowest=True),
        observed=True
    ).size().reset_index(name='total')
    total_by_bucket.columns = ['discount_bucket', 'total']  # Rename column
    
    grouped = grouped.merge(
        total_by_bucket,
        on='discount_bucket',
        how='left'
    )
    grouped['conversion_rate'] = (grouped['product_id'] / grouped['total'] * 100).fillna(0)
    
    # Convert to schema
    result = []
    for _, row in grouped.iterrows():
        result.append(DiscountVsUnitsDataPoint(
            discount_range=str(row['discount_bucket']),
            discount_avg=Decimal(str(round(row['discount_pct'], 2))),
            total_units_sold=int(row['units_sold']),
            total_revenue=Decimal(str(round(row['revenue'], 2))),
            transaction_count=int(row['product_id']),
            conversion_rate=Decimal(str(round(row['conversion_rate'], 2)))
        ))
    
    return result


def aggregate_category_performance(df: pd.DataFrame) -> List[CategoryPerformance]:
    """Aggregate performance by product category."""
    sold_df = df[df['sold'] == 1].copy()
    
    if sold_df.empty:
        return []
    
    # Group by category
    grouped = sold_df.groupby('category').agg({
        'units_sold': 'sum',
        'base_price': 'sum',
        'discount_pct': 'mean'
    }).reset_index()
    
    # Calculate revenue
    grouped['revenue'] = grouped['base_price'] * (1 - grouped['discount_pct'] / 100)
    
    # Sort by revenue
    grouped = grouped.sort_values('revenue', ascending=False)
    
    # Convert to schema
    result = []
    for _, row in grouped.iterrows():
        result.append(CategoryPerformance(
            category=row['category'],
            total_units_sold=int(row['units_sold']),
            total_revenue=Decimal(str(round(row['revenue'], 2))),
            avg_discount_pct=Decimal(str(round(row['discount_pct'], 2)))
        ))
    
    return result


def calculate_summary(df: pd.DataFrame) -> AnalyticsSummary:
    """Calculate overall summary statistics."""
    sold_df = df[df['sold'] == 1].copy()
    
    if sold_df.empty:
        return AnalyticsSummary(
            total_revenue=Decimal("0.00"),
            total_units_sold=0,
            avg_discount_pct=Decimal("0.00"),
            products_with_discount=0,
            products_expiring_soon=0
        )
    
    # Calculate metrics
    total_units = int(sold_df['units_sold'].sum())
    avg_discount = float(sold_df['discount_pct'].mean())
    
    # Revenue calculation
    revenue = (sold_df['base_price'] * (1 - sold_df['discount_pct'] / 100)).sum()
    
    # Products with discount (discount > 0)
    products_with_discount = int((df['discount_pct'] > 0).sum())
    
    # Products expiring soon (days_to_expiry <= 7)
    products_expiring_soon = int((df['days_to_expiry'] <= 7).sum())
    
    return AnalyticsSummary(
        total_revenue=Decimal(str(round(revenue, 2))),
        total_units_sold=total_units,
        avg_discount_pct=Decimal(str(round(avg_discount, 2))),
        products_with_discount=products_with_discount,
        products_expiring_soon=products_expiring_soon
    )


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard():
    """
    Get complete analytics dashboard data.
    
    Returns:
    - Summary statistics
    - Sales vs Expiry data points
    - Discount vs Units Sold data points
    - Category performance metrics
    
    Note: Currently uses synthetic data. In production, this would query
    actual sales transactions from the database.
    """
    try:
        # Load data
        df = load_synthetic_data()
        
        # Generate all analytics
        summary = calculate_summary(df)
        sales_vs_expiry = aggregate_sales_vs_expiry(df)
        discount_vs_units = aggregate_discount_vs_units(df)
        category_performance = aggregate_category_performance(df)
        
        return AnalyticsDashboardResponse(
            summary=summary,
            sales_vs_expiry=sales_vs_expiry,
            discount_vs_units=discount_vs_units,
            category_performance=category_performance
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )


@router.get("/sales-vs-expiry", response_model=List[SalesVsExpiryDataPoint])
async def get_sales_vs_expiry(
    max_days: int = Query(default=30, ge=1, le=365, description="Maximum days to expiry to include")
):
    """
    Get sales vs expiry data for charting.
    
    Shows relationship between days until expiry and sales performance.
    """
    try:
        df = load_synthetic_data()
        
        # Filter by max_days
        df = df[df['days_to_expiry'] <= max_days]
        
        return aggregate_sales_vs_expiry(df)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales vs expiry data: {str(e)}"
        )


@router.get("/discount-vs-units", response_model=List[DiscountVsUnitsDataPoint])
async def get_discount_vs_units():
    """
    Get discount vs units sold data for charting.
    
    Shows relationship between discount percentage and units sold.
    Includes conversion rates for each discount bucket.
    """
    try:
        df = load_synthetic_data()
        return aggregate_discount_vs_units(df)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get discount vs units data: {str(e)}"
        )


@router.get("/category-performance", response_model=List[CategoryPerformance])
async def get_category_performance():
    """
    Get performance metrics by product category.
    
    Shows which categories generate most revenue and sales.
    """
    try:
        df = load_synthetic_data()
        return aggregate_category_performance(df)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get category performance: {str(e)}"
        )
