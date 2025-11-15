"""
Quick data exploration script for synthetic purchase data.
Performs basic statistical analysis and data quality checks.

Usage:
    python3 scripts/explore_data.py data/synthetic_purchases.csv
"""

import argparse
import csv
from collections import defaultdict
from typing import Dict, List


def load_csv(filepath: str) -> List[Dict]:
    """Load CSV file into list of dictionaries."""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def analyze_basic_stats(data: List[Dict]):
    """Print basic statistics about the dataset."""
    print("\n" + "="*70)
    print("BASIC STATISTICS")
    print("="*70)
    
    total = len(data)
    sold = sum(1 for row in data if row['sold'] == '1')
    
    print(f"Total records:       {total:,}")
    print(f"Sold records:        {sold:,} ({sold/total*100:.1f}%)")
    print(f"Not sold records:    {total-sold:,} ({(total-sold)/total*100:.1f}%)")
    
    # Numeric stats
    total_revenue = sum(float(row['revenue']) for row in data)
    total_units = sum(int(row['units_sold']) for row in data)
    avg_discount = sum(float(row['discount_pct']) for row in data) / total
    avg_price = sum(float(row['base_price']) for row in data) / total
    
    print(f"\nTotal revenue:       ${total_revenue:,.2f}")
    print(f"Total units sold:    {total_units:,}")
    print(f"Avg discount:        {avg_discount:.2f}%")
    print(f"Avg base price:      ${avg_price:.2f}")
    
    if sold > 0:
        avg_units_per_sale = total_units / sold
        avg_revenue_per_sale = total_revenue / sold
        print(f"Avg units/sale:      {avg_units_per_sale:.2f}")
        print(f"Avg revenue/sale:    ${avg_revenue_per_sale:.2f}")


def analyze_by_category(data: List[Dict]):
    """Analyze statistics by product category."""
    print("\n" + "="*70)
    print("CATEGORY ANALYSIS")
    print("="*70)
    
    categories = defaultdict(lambda: {
        'count': 0, 'sold': 0, 'revenue': 0, 'units': 0,
        'total_discount': 0, 'total_price': 0
    })
    
    for row in data:
        cat = row['category']
        categories[cat]['count'] += 1
        categories[cat]['total_discount'] += float(row['discount_pct'])
        categories[cat]['total_price'] += float(row['base_price'])
        
        if row['sold'] == '1':
            categories[cat]['sold'] += 1
            categories[cat]['revenue'] += float(row['revenue'])
            categories[cat]['units'] += int(row['units_sold'])
    
    print(f"{'Category':<12} {'Count':>6} {'Conv%':>7} {'Revenue':>12} {'AvgDisc%':>9} {'AvgPrice':>9}")
    print("-" * 70)
    
    for cat in sorted(categories.keys()):
        stats = categories[cat]
        conv_rate = (stats['sold'] / stats['count'] * 100) if stats['count'] > 0 else 0
        avg_discount = stats['total_discount'] / stats['count'] if stats['count'] > 0 else 0
        avg_price = stats['total_price'] / stats['count'] if stats['count'] > 0 else 0
        
        print(f"{cat:<12} {stats['count']:>6} {conv_rate:>6.1f}% "
              f"${stats['revenue']:>10,.2f} {avg_discount:>8.1f}% "
              f"${avg_price:>8.2f}")


def analyze_discount_bins(data: List[Dict]):
    """Analyze conversion by discount percentage bins."""
    print("\n" + "="*70)
    print("DISCOUNT BIN ANALYSIS")
    print("="*70)
    
    bins = {
        '0-10%': (0, 10),
        '10-20%': (10, 20),
        '20-30%': (20, 30),
        '30-40%': (30, 40),
        '40-50%': (40, 50),
    }
    
    bin_stats = defaultdict(lambda: {'count': 0, 'sold': 0, 'revenue': 0})
    
    for row in data:
        discount = float(row['discount_pct'])
        for bin_name, (low, high) in bins.items():
            if low <= discount < high:
                bin_stats[bin_name]['count'] += 1
                if row['sold'] == '1':
                    bin_stats[bin_name]['sold'] += 1
                    bin_stats[bin_name]['revenue'] += float(row['revenue'])
                break
    
    print(f"{'Discount Range':<15} {'Count':>6} {'Conv%':>7} {'Revenue':>12}")
    print("-" * 70)
    
    for bin_name in ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%']:
        stats = bin_stats[bin_name]
        if stats['count'] > 0:
            conv_rate = stats['sold'] / stats['count'] * 100
            print(f"{bin_name:<15} {stats['count']:>6} {conv_rate:>6.1f}% "
                  f"${stats['revenue']:>10,.2f}")


def analyze_expiry_impact(data: List[Dict]):
    """Analyze conversion by days to expiry."""
    print("\n" + "="*70)
    print("EXPIRY IMPACT ANALYSIS")
    print("="*70)
    
    expiry_bins = {
        '1-3 days': (1, 3),
        '4-7 days': (4, 7),
        '8-14 days': (8, 14),
        '15-30 days': (15, 30),
        '30+ days': (31, 9999),
    }
    
    bin_stats = defaultdict(lambda: {'count': 0, 'sold': 0, 'avg_discount': 0})
    
    for row in data:
        days = int(row['days_to_expiry'])
        for bin_name, (low, high) in expiry_bins.items():
            if low <= days <= high:
                bin_stats[bin_name]['count'] += 1
                bin_stats[bin_name]['avg_discount'] += float(row['discount_pct'])
                if row['sold'] == '1':
                    bin_stats[bin_name]['sold'] += 1
                break
    
    print(f"{'Days to Expiry':<15} {'Count':>6} {'Conv%':>7} {'AvgDisc%':>9}")
    print("-" * 70)
    
    for bin_name in ['1-3 days', '4-7 days', '8-14 days', '15-30 days', '30+ days']:
        stats = bin_stats[bin_name]
        if stats['count'] > 0:
            conv_rate = stats['sold'] / stats['count'] * 100
            avg_discount = stats['avg_discount'] / stats['count']
            print(f"{bin_name:<15} {stats['count']:>6} {conv_rate:>6.1f}% {avg_discount:>8.1f}%")


def analyze_day_of_week(data: List[Dict]):
    """Analyze conversion by day of week."""
    print("\n" + "="*70)
    print("DAY OF WEEK ANALYSIS")
    print("="*70)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = defaultdict(lambda: {'count': 0, 'sold': 0, 'revenue': 0})
    
    for row in data:
        day_idx = int(row['day_of_week'])
        day_name = days[day_idx]
        day_stats[day_name]['count'] += 1
        if row['sold'] == '1':
            day_stats[day_name]['sold'] += 1
            day_stats[day_name]['revenue'] += float(row['revenue'])
    
    print(f"{'Day':<12} {'Count':>6} {'Conv%':>7} {'Revenue':>12}")
    print("-" * 70)
    
    for day in days:
        stats = day_stats[day]
        if stats['count'] > 0:
            conv_rate = stats['sold'] / stats['count'] * 100
            print(f"{day:<12} {stats['count']:>6} {conv_rate:>6.1f}% ${stats['revenue']:>10,.2f}")


def check_data_quality(data: List[Dict]):
    """Check for data quality issues."""
    print("\n" + "="*70)
    print("DATA QUALITY CHECKS")
    print("="*70)
    
    issues = []
    
    # Check for missing values
    required_fields = ['product_id', 'category', 'base_price', 'discount_pct', 
                      'days_to_expiry', 'sold', 'units_sold']
    
    for field in required_fields:
        missing = sum(1 for row in data if not row.get(field))
        if missing > 0:
            issues.append(f"  ✗ Missing {field}: {missing} records")
    
    # Check for logical inconsistencies
    sold_but_no_units = sum(1 for row in data 
                           if row['sold'] == '1' and int(row['units_sold']) == 0)
    if sold_but_no_units > 0:
        issues.append(f"  ✗ Sold but no units: {sold_but_no_units} records")
    
    not_sold_but_units = sum(1 for row in data 
                            if row['sold'] == '0' and int(row['units_sold']) > 0)
    if not_sold_but_units > 0:
        issues.append(f"  ✗ Not sold but has units: {not_sold_but_units} records")
    
    negative_prices = sum(1 for row in data if float(row['base_price']) < 0)
    if negative_prices > 0:
        issues.append(f"  ✗ Negative prices: {negative_prices} records")
    
    invalid_discounts = sum(1 for row in data 
                           if float(row['discount_pct']) < 0 or float(row['discount_pct']) > 100)
    if invalid_discounts > 0:
        issues.append(f"  ✗ Invalid discounts: {invalid_discounts} records")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("✓ All quality checks passed!")
    
    # Summary stats
    unique_products = len(set(row['product_id'] for row in data))
    date_range_start = min(row['timestamp'] for row in data)
    date_range_end = max(row['timestamp'] for row in data)
    
    print(f"\n✓ Unique products:   {unique_products}")
    print(f"✓ Date range:        {date_range_start[:10]} to {date_range_end[:10]}")


def main():
    parser = argparse.ArgumentParser(
        description="Explore synthetic purchase data"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input CSV file path"
    )
    
    args = parser.parse_args()
    
    print(f"\nLoading data from {args.input}...")
    data = load_csv(args.input)
    print(f"✓ Loaded {len(data):,} records")
    
    # Run all analyses
    analyze_basic_stats(data)
    analyze_by_category(data)
    analyze_discount_bins(data)
    analyze_expiry_impact(data)
    analyze_day_of_week(data)
    check_data_quality(data)
    
    print("\n" + "="*70)
    print("EXPLORATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
