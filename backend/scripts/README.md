# Backend Scripts

Setup, utility, and ML data generation scripts for FlexiPrice.

## Database Scripts

### `init_db.py`
Initialize the database schema and create necessary tables.

```bash
python3 scripts/init_db.py
```

## Validation Scripts

### `validate_features.py`
Validate backend features and API endpoints.

```bash
python3 scripts/validate_features.py
```

## Background Task Management

### `celery_manager.py`
Manage Celery workers and beat scheduler for background tasks.

```bash
python3 scripts/celery_manager.py
```

## ML Data Generation (Week 4)

### `generate_synthetic_data.py`
Generate synthetic purchase event logs for ML model training.

**Features:**
- Realistic purchase patterns with noise
- 8 product categories with different characteristics
- Temporal features (day of week, seasonality)
- Discount, expiry, and inventory effects
- Binary target (sold) and units_sold

**Usage:**
```bash
# Generate 10,000 events (default)
python3 scripts/generate_synthetic_data.py

# Custom generation
python3 scripts/generate_synthetic_data.py \
  --samples 50000 \
  --output data/training_data.csv \
  --start-date 2023-01-01 \
  --days 730 \
  --seed 42
```

**Options:**
- `--samples`: Number of events to generate (default: 10000)
- `--output`: Output CSV file path (default: data/synthetic_purchases.csv)
- `--start-date`: Start date YYYY-MM-DD (default: 2024-01-01)
- `--days`: Number of days to spread events (default: 365)
- `--seed`: Random seed for reproducibility (default: 42)

### `explore_data.py`
Perform statistical analysis and data quality checks on generated data.

**Analyses:**
- Basic statistics (conversion, revenue, units)
- Category breakdown
- Discount bin analysis
- Expiry impact analysis
- Day of week patterns
- Data quality checks

**Usage:**
```bash
python3 scripts/explore_data.py data/synthetic_purchases.csv
```

### `visualize_data.py`
Create visualizations of the synthetic data (requires matplotlib and pandas).

**Plots generated:**
- Conversion rate by discount range
- Category performance (conversion + revenue)
- Expiry urgency effect
- Day of week patterns
- Feature correlation heatmap

**Installation:**
```bash
pip install matplotlib pandas
```

**Usage:**
```bash
python3 scripts/visualize_data.py data/synthetic_purchases.csv --output-dir data/visualizations
```

### `generate_datasets.sh`
Batch generate multiple dataset sizes for experimentation.

**Datasets created:**
- Small: 5,000 events (quick testing)
- Medium: 20,000 events (model training)
- Large: 50,000 events (robust training)
- Multi-year: 100,000 events over 2 years

**Usage:**
```bash
./scripts/generate_datasets.sh
```

## Quick Start for ML Development

```bash
# 1. Generate training data
python3 scripts/generate_synthetic_data.py --samples 20000

# 2. Explore the data
python3 scripts/explore_data.py data/synthetic_purchases.csv

# 3. (Optional) Create visualizations
pip install matplotlib pandas
python3 scripts/visualize_data.py data/synthetic_purchases.csv

# 4. Ready for model training!
# See Week 4 documentation for ML model development
```

## Data Files

Generated data is stored in `backend/data/`:
- `synthetic_purchases.csv` - Default 10K events
- `synthetic_small.csv` - 5K events
- `synthetic_medium.csv` - 20K events
- `synthetic_large.csv` - 50K events
- `synthetic_multiyear.csv` - 100K events (2 years)

See `backend/data/README.md` for detailed data documentation.
