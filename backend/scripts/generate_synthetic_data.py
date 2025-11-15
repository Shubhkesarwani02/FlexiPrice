"""
Data Simulation Script for ML Training
Generates synthetic purchase event logs with realistic patterns and noise.

Features generated:
- product_id, base_price, category, days_to_expiry
- discount_pct, inventory_level, day_of_week, seasonality flags
- sold (binary target), units_sold

Usage:
    python generate_synthetic_data.py --samples 10000 --output data/synthetic_purchases.csv
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math


# Product categories with realistic price ranges
CATEGORIES = {
    "Dairy": {"price_range": (2.0, 15.0), "shelf_life": (3, 14), "seasonality": "low"},
    "Bakery": {"price_range": (1.5, 10.0), "shelf_life": (1, 7), "seasonality": "low"},
    "Meat": {"price_range": (5.0, 40.0), "shelf_life": (2, 10), "seasonality": "low"},
    "Seafood": {"price_range": (8.0, 50.0), "shelf_life": (1, 5), "seasonality": "high"},
    "Produce": {"price_range": (1.0, 20.0), "shelf_life": (3, 14), "seasonality": "high"},
    "Frozen": {"price_range": (3.0, 25.0), "shelf_life": (30, 180), "seasonality": "medium"},
    "Beverages": {"price_range": (1.0, 15.0), "shelf_life": (30, 365), "seasonality": "medium"},
    "Snacks": {"price_range": (2.0, 12.0), "shelf_life": (14, 180), "seasonality": "low"},
}

# Seasonality multipliers by month (1-12)
SEASONAL_MULTIPLIERS = {
    "high": [0.8, 0.7, 0.9, 1.0, 1.1, 1.3, 1.4, 1.3, 1.0, 0.9, 0.8, 0.9],
    "medium": [0.9, 0.9, 1.0, 1.0, 1.05, 1.1, 1.15, 1.1, 1.0, 1.0, 0.95, 1.0],
    "low": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
}


def generate_product_id(idx: int, category: str) -> str:
    """Generate unique product ID."""
    category_code = category[:3].upper()
    return f"{category_code}-{idx:05d}"


def calculate_purchase_probability(
    discount_pct: float,
    days_to_expiry: int,
    inventory_level: int,
    base_price: float,
    day_of_week: int,
    season_multiplier: float,
) -> float:
    """
    Calculate realistic purchase probability based on multiple factors.
    
    Key insights:
    - Higher discount = higher probability (diminishing returns after 30%)
    - Closer to expiry = higher urgency (especially last 3 days)
    - Lower inventory = higher scarcity effect
    - Price sensitivity varies
    - Weekend effect (Fri-Sun higher traffic)
    - Seasonality matters
    """
    
    # Base probability
    prob = 0.15  # 15% baseline purchase rate
    
    # Discount effect (sigmoid curve, plateaus after 40%)
    discount_effect = 1 / (1 + math.exp(-0.15 * (discount_pct - 20)))
    prob += discount_effect * 0.4
    
    # Days to expiry urgency (exponential increase as expiry nears)
    if days_to_expiry <= 3:
        urgency = 0.35 * (1 - days_to_expiry / 3)
    elif days_to_expiry <= 7:
        urgency = 0.20 * (1 - days_to_expiry / 7)
    else:
        urgency = 0.05 * (1 - min(days_to_expiry, 30) / 30)
    prob += urgency
    
    # Inventory scarcity effect
    if inventory_level < 10:
        scarcity = 0.15 * (1 - inventory_level / 10)
    elif inventory_level < 50:
        scarcity = 0.05 * (1 - inventory_level / 50)
    else:
        scarcity = 0.0
    prob += scarcity
    
    # Price sensitivity (higher prices slightly reduce probability)
    price_factor = 1.0 - (min(base_price, 50) / 100) * 0.1
    prob *= price_factor
    
    # Day of week effect (0=Mon, 6=Sun)
    weekend_multiplier = [0.95, 0.95, 0.98, 1.00, 1.10, 1.15, 1.12][day_of_week]
    prob *= weekend_multiplier
    
    # Seasonality
    prob *= season_multiplier
    
    # Add some random noise (±10%)
    noise = random.uniform(-0.05, 0.05)
    prob += noise
    
    # Clamp between 0 and 1
    return max(0.0, min(1.0, prob))


def calculate_units_sold(
    sold: bool,
    purchase_prob: float,
    inventory_level: int,
    discount_pct: float,
) -> int:
    """Calculate units sold based on purchase probability and other factors."""
    if not sold:
        return 0
    
    # Base units: higher probability = more units
    base_units = 1 + int(purchase_prob * 5)
    
    # Bulk purchase effect at high discounts
    if discount_pct >= 30:
        bulk_multiplier = 1 + (discount_pct - 30) / 100
        base_units = int(base_units * bulk_multiplier)
    
    # Limit by inventory
    max_units = min(inventory_level, 10)  # Rarely sell more than 10 units at once
    
    units = min(base_units, max_units)
    
    # Add some randomness
    if random.random() < 0.3:  # 30% chance of +1 unit
        units = min(units + 1, max_units)
    
    return max(1, units)


def generate_synthetic_event(
    event_id: int,
    start_date: datetime,
    num_days: int,
) -> Dict:
    """Generate a single synthetic purchase event."""
    
    # Random date within the range
    days_offset = random.randint(0, num_days - 1)
    event_date = start_date + timedelta(days=days_offset)
    
    # Select category and product
    category = random.choice(list(CATEGORIES.keys()))
    cat_info = CATEGORIES[category]
    product_id = generate_product_id(
        random.randint(1, 200),  # ~200 unique products
        category
    )
    
    # Generate base price
    price_min, price_max = cat_info["price_range"]
    base_price = round(random.uniform(price_min, price_max), 2)
    
    # Days to expiry
    shelf_min, shelf_max = cat_info["shelf_life"]
    days_to_expiry = random.randint(shelf_min, shelf_max)
    
    # Discount percentage (weighted towards lower discounts)
    discount_weights = [0.30, 0.25, 0.20, 0.15, 0.10]  # 0-10%, 10-20%, etc.
    discount_bracket = random.choices([0, 1, 2, 3, 4], weights=discount_weights)[0]
    discount_pct = round(random.uniform(discount_bracket * 10, (discount_bracket + 1) * 10), 1)
    
    # Inventory level (skewed towards higher inventory)
    inventory_level = int(random.lognormvariate(3.5, 0.8))  # Mean ~50, some very high
    inventory_level = max(1, min(inventory_level, 500))
    
    # Day of week and seasonality
    day_of_week = event_date.weekday()  # 0=Monday, 6=Sunday
    month = event_date.month
    seasonality = cat_info["seasonality"]
    season_multiplier = SEASONAL_MULTIPLIERS[seasonality][month - 1]
    
    # Calculate purchase probability
    purchase_prob = calculate_purchase_probability(
        discount_pct=discount_pct,
        days_to_expiry=days_to_expiry,
        inventory_level=inventory_level,
        base_price=base_price,
        day_of_week=day_of_week,
        season_multiplier=season_multiplier,
    )
    
    # Determine if sold
    sold = random.random() < purchase_prob
    
    # Calculate units sold
    units_sold = calculate_units_sold(
        sold=sold,
        purchase_prob=purchase_prob,
        inventory_level=inventory_level,
        discount_pct=discount_pct,
    )
    
    # Seasonality flags
    is_summer = 1 if month in [6, 7, 8] else 0
    is_winter = 1 if month in [12, 1, 2] else 0
    is_holiday_season = 1 if month in [11, 12] else 0
    
    return {
        "event_id": event_id,
        "timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
        "product_id": product_id,
        "category": category,
        "base_price": base_price,
        "discount_pct": discount_pct,
        "discounted_price": round(base_price * (1 - discount_pct / 100), 2),
        "days_to_expiry": days_to_expiry,
        "inventory_level": inventory_level,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": 1 if day_of_week >= 5 else 0,
        "is_summer": is_summer,
        "is_winter": is_winter,
        "is_holiday_season": is_holiday_season,
        "season_multiplier": round(season_multiplier, 3),
        "sold": 1 if sold else 0,
        "units_sold": units_sold,
        "revenue": round(base_price * (1 - discount_pct / 100) * units_sold, 2) if sold else 0,
    }


def generate_dataset(
    num_samples: int,
    start_date: datetime,
    num_days: int = 365,
) -> List[Dict]:
    """Generate complete synthetic dataset."""
    print(f"Generating {num_samples} synthetic purchase events...")
    print(f"Date range: {start_date.date()} to {(start_date + timedelta(days=num_days)).date()}")
    
    events = []
    for i in range(num_samples):
        event = generate_synthetic_event(i + 1, start_date, num_days)
        events.append(event)
        
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1}/{num_samples} events...")
    
    return events


def save_to_csv(events: List[Dict], output_path: str):
    """Save events to CSV file."""
    if not events:
        print("No events to save!")
        return
    
    fieldnames = list(events[0].keys())
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)
    
    print(f"\n✓ Saved {len(events)} events to {output_path}")


def print_statistics(events: List[Dict]):
    """Print dataset statistics."""
    total = len(events)
    sold_count = sum(1 for e in events if e["sold"] == 1)
    total_revenue = sum(e["revenue"] for e in events)
    total_units = sum(e["units_sold"] for e in events)
    
    avg_discount = sum(e["discount_pct"] for e in events) / total
    avg_price = sum(e["base_price"] for e in events) / total
    
    print("\n" + "="*60)
    print("DATASET STATISTICS")
    print("="*60)
    print(f"Total events:        {total:,}")
    print(f"Sold events:         {sold_count:,} ({sold_count/total*100:.1f}%)")
    print(f"Not sold:            {total-sold_count:,} ({(total-sold_count)/total*100:.1f}%)")
    print(f"Total units sold:    {total_units:,}")
    print(f"Total revenue:       ${total_revenue:,.2f}")
    print(f"Avg discount:        {avg_discount:.1f}%")
    print(f"Avg base price:      ${avg_price:.2f}")
    
    print("\nCategory breakdown:")
    categories = {}
    for event in events:
        cat = event["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "sold": 0}
        categories[cat]["count"] += 1
        if event["sold"] == 1:
            categories[cat]["sold"] += 1
    
    for cat, stats in sorted(categories.items()):
        conversion = stats["sold"] / stats["count"] * 100
        print(f"  {cat:12} - {stats['count']:5} events, {conversion:5.1f}% conversion")
    
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic purchase event data for ML training"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=10000,
        help="Number of synthetic events to generate (default: 10000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/synthetic_purchases.csv",
        help="Output CSV file path (default: data/synthetic_purchases.csv)"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2024-01-01",
        help="Start date for events (YYYY-MM-DD, default: 2024-01-01)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days to spread events over (default: 365)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    # Parse start date
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    
    # Generate dataset
    events = generate_dataset(args.samples, start_date, args.days)
    
    # Print statistics
    print_statistics(events)
    
    # Save to CSV
    save_to_csv(events, args.output)
    
    print(f"✓ Data generation complete!")
    print(f"\nYou can now use this data for ML model training.")
    print(f"Next steps:")
    print(f"  1. Explore the data: head {args.output}")
    print(f"  2. Train XGBoost model on this data")
    print(f"  3. Evaluate model performance")


if __name__ == "__main__":
    main()
