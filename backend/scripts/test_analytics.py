"""
Test script for analytics API endpoints.
Validates that analytics data is correctly aggregated and returned.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import pandas as pd
from app.api.v1.endpoints.analytics import (
    load_synthetic_data,
    aggregate_sales_vs_expiry,
    aggregate_discount_vs_units,
    aggregate_category_performance,
    calculate_summary,
)


def test_analytics():
    """Test all analytics aggregation functions."""
    
    print("=" * 60)
    print("ANALYTICS API TEST")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading synthetic data...")
    try:
        df = load_synthetic_data()
        print(f"   ✓ Loaded {len(df)} records")
        print(f"   - Sold: {df['sold'].sum()} ({df['sold'].mean()*100:.1f}%)")
        print(f"   - Categories: {df['category'].nunique()}")
    except Exception as e:
        print(f"   ✗ Failed to load data: {e}")
        return
    
    # Test summary
    print("\n2. Testing summary statistics...")
    try:
        summary = calculate_summary(df)
        print(f"   ✓ Summary generated")
        print(f"   - Total Revenue: ${summary.total_revenue}")
        print(f"   - Total Units Sold: {summary.total_units_sold}")
        print(f"   - Avg Discount: {summary.avg_discount_pct}%")
        print(f"   - Products with Discount: {summary.products_with_discount}")
        print(f"   - Expiring Soon (≤7 days): {summary.products_expiring_soon}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test sales vs expiry
    print("\n3. Testing sales vs expiry aggregation...")
    try:
        sales_data = aggregate_sales_vs_expiry(df)
        print(f"   ✓ Generated {len(sales_data)} data points")
        if sales_data:
            print(f"   - Days range: {sales_data[0].days_to_expiry} to {sales_data[-1].days_to_expiry}")
            top_3 = sorted(sales_data, key=lambda x: x.total_units_sold, reverse=True)[:3]
            print(f"   - Top 3 by units sold:")
            for item in top_3:
                print(f"     • {item.days_to_expiry} days: {item.total_units_sold} units, ${item.total_revenue}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test discount vs units
    print("\n4. Testing discount vs units aggregation...")
    try:
        discount_data = aggregate_discount_vs_units(df)
        print(f"   ✓ Generated {len(discount_data)} discount buckets")
        if discount_data:
            print(f"   - Discount ranges:")
            for item in discount_data:
                print(f"     • {item.discount_range}: {item.total_units_sold} units, "
                      f"{item.conversion_rate:.1f}% conversion")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test category performance
    print("\n5. Testing category performance aggregation...")
    try:
        category_data = aggregate_category_performance(df)
        print(f"   ✓ Generated {len(category_data)} categories")
        if category_data:
            print(f"   - Top 3 by revenue:")
            for item in category_data[:3]:
                print(f"     • {item.category}: ${item.total_revenue} revenue, "
                      f"{item.total_units_sold} units")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_analytics()
