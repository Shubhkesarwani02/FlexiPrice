# Data Simulation for ML Training

## Overview

This directory contains scripts and data for the ML-powered discount optimization system.

## Synthetic Data Generation

### Script: `generate_synthetic_data.py`

Generates realistic purchase event logs with the following features:

**Product Features:**
- `product_id`: Unique product identifier (e.g., DAI-00123)
- `category`: Product category (Dairy, Bakery, Meat, Seafood, Produce, Frozen, Beverages, Snacks)
- `base_price`: Original product price ($)
- `discounted_price`: Price after discount ($)

**Discount & Inventory:**
- `discount_pct`: Discount percentage (0-50%)
- `days_to_expiry`: Days until product expires (1-365 depending on category)
- `inventory_level`: Current stock level (1-500 units)

**Temporal Features:**
- `timestamp`: Event date and time
- `day_of_week`: Day of week (0=Monday, 6=Sunday)
- `month`: Month (1-12)
- `is_weekend`: Binary flag for weekend days
- `is_summer`: Binary flag for summer months (Jun-Aug)
- `is_winter`: Binary flag for winter months (Dec-Feb)
- `is_holiday_season`: Binary flag for holiday season (Nov-Dec)
- `season_multiplier`: Seasonality adjustment factor

**Target Variables:**
- `sold`: Binary indicator (1=sold, 0=not sold)
- `units_sold`: Number of units sold (0-10)
- `revenue`: Total revenue generated ($)

### Realistic Patterns Implemented

1. **Discount Effect**: Sigmoid curve with diminishing returns after 30-40%
2. **Urgency**: Exponential increase in purchase probability as expiry nears (especially last 3 days)
3. **Scarcity**: Low inventory creates urgency (<10 units has strong effect)
4. **Price Sensitivity**: Higher-priced items have slightly lower purchase probability
5. **Weekend Effect**: 10-15% higher conversion on Fri-Sun
6. **Seasonality**: Category-specific seasonal patterns (e.g., Seafood peaks in summer)
7. **Noise**: Random variation to simulate real-world unpredictability

### Usage

```bash
# Generate 10,000 events (default)
python3 scripts/generate_synthetic_data.py

# Generate custom dataset
python3 scripts/generate_synthetic_data.py \
  --samples 50000 \
  --output data/large_dataset.csv \
  --start-date 2023-01-01 \
  --days 730 \
  --seed 123

# Options:
#   --samples: Number of events to generate (default: 10000)
#   --output: Output CSV file path (default: data/synthetic_purchases.csv)
#   --start-date: Start date YYYY-MM-DD (default: 2024-01-01)
#   --days: Number of days to spread events (default: 365)
#   --seed: Random seed for reproducibility (default: 42)
```

### Example Output Statistics

```
Total events:        10,000
Sold events:         4,033 (40.3%)
Not sold:            5,967 (59.7%)
Total units sold:    12,760
Total revenue:       $127,600.16
Avg discount:        19.9%
Avg base price:      $13.01

Category breakdown:
  Bakery       -  1287 events,  42.7% conversion
  Beverages    -  1243 events,  35.6% conversion
  Dairy        -  1224 events,  41.5% conversion
  Frozen       -  1215 events,  39.3% conversion
  Meat         -  1272 events,  40.9% conversion
  Produce      -  1260 events,  41.0% conversion
  Seafood      -  1206 events,  46.3% conversion
  Snacks       -  1293 events,  35.7% conversion
```

## Data Files

- `synthetic_purchases.csv`: Generated training data for ML model

## Next Steps

1. **Day 2**: Exploratory Data Analysis (EDA)
   - Analyze feature correlations
   - Visualize discount vs. conversion patterns
   - Identify key drivers of purchase probability

2. **Day 3**: Feature engineering and model training
   - Train XGBoost classifier for purchase prediction
   - Tune hyperparameters
   - Evaluate model performance

3. **Day 4**: Model optimization and discount recommendations
   - Build uplift model
   - Create discount recommendation engine
   - Test different discount strategies

4. **Day 5**: Integration with backend API
   - Create `ml_predictor` service
   - Add `/api/v1/ml/recommend-discount` endpoint
   - Integrate with admin dashboard
