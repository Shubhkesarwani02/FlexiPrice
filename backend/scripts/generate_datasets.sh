#!/bin/bash

# Generate multiple dataset sizes for ML experimentation
# Usage: ./generate_datasets.sh

echo "Generating synthetic datasets for ML training..."
echo ""

# Create data directory if it doesn't exist
mkdir -p data

# Small dataset for quick testing (5K events)
echo "1. Generating small dataset (5,000 events)..."
python3 scripts/generate_synthetic_data.py \
  --samples 5000 \
  --output data/synthetic_small.csv \
  --seed 42

# Medium dataset for model training (20K events)
echo ""
echo "2. Generating medium dataset (20,000 events)..."
python3 scripts/generate_synthetic_data.py \
  --samples 20000 \
  --output data/synthetic_medium.csv \
  --seed 123

# Large dataset for robust training (50K events)
echo ""
echo "3. Generating large dataset (50,000 events)..."
python3 scripts/generate_synthetic_data.py \
  --samples 50000 \
  --output data/synthetic_large.csv \
  --seed 456

# Multi-year dataset for time series analysis (100K events over 2 years)
echo ""
echo "4. Generating multi-year dataset (100,000 events)..."
python3 scripts/generate_synthetic_data.py \
  --samples 100000 \
  --output data/synthetic_multiyear.csv \
  --start-date 2023-01-01 \
  --days 730 \
  --seed 789

echo ""
echo "✓ All datasets generated successfully!"
echo ""
echo "Dataset sizes:"
ls -lh data/*.csv | awk '{print "  " $9 " - " $5}'
echo ""
echo "You can now:"
echo "  - Explore data: python3 scripts/explore_data.py data/synthetic_medium.csv"
echo "  - Train models: Use any dataset for XGBoost training"
echo "  - Compare: Test model performance across different dataset sizes"
