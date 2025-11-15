# XGBoost Purchase Prediction Model

## Model Overview

**Type**: Binary Classification (XGBoost)  
**Task**: Predict purchase probability (will customer buy at given discount?)  
**Training Date**: 2025-11-15  
**Framework**: XGBoost 2.1.4

## Performance Metrics

### Test Set Performance (2,000 samples)

| Metric | Score |
|--------|-------|
| **Accuracy** | 65.15% |
| **ROC-AUC** | 0.6724 |
| **Precision** | 0.6046 |
| **Recall** | 0.3941 |
| **F1-Score** | 0.4771 |

### Confusion Matrix

```
                Predicted
              Not Sold  Sold
Actual Not Sold    985    208  (83% recall)
       Sold        489    318  (39% recall)
```

**Interpretation:**
- Model is conservative (higher precision, lower recall)
- Better at identifying "Not Sold" cases (83% recall)
- Misses 61% of actual purchases (false negatives)
- Good for scenarios where false positives are costly

## Features (20 total)

### Base Features (11)
1. `base_price` - Original product price
2. `discount_pct` - Discount percentage
3. `days_to_expiry` - Days until expiration
4. `inventory_level` - Current stock quantity
5. `day_of_week` - Day of week (0=Mon, 6=Sun)
6. `month` - Month (1-12)
7. `is_weekend` - Weekend flag
8. `is_summer` - Summer months flag
9. `is_winter` - Winter months flag
10. `is_holiday_season` - Holiday season flag
11. `season_multiplier` - Seasonality adjustment

### Engineered Features (9)
12. `urgency_score` - Combined expiry + scarcity urgency
13. `discount_per_day` - Discount effectiveness per day
14. `inventory_risk` - Low stock + near expiry flag
15. `high_urgency` - ≤3 days to expiry flag
16. `deep_discount` - ≥30% discount flag
17. `discount_expiry_interaction` - Discount × expiry interaction
18. `price_discount_ratio` - Discount relative to price
19. `category_encoded` - Product category (8 categories)
20. `price_tier_encoded` - Price tier: low/medium/high

## Feature Importance (Top 10)

Measured by information gain:

| Rank | Feature | Importance | Insight |
|------|---------|-----------|---------|
| 1 | `deep_discount` | 112.72 | **Most critical**: ≥30% discounts drive purchases |
| 2 | `discount_pct` | 18.35 | Primary driver of purchase decision |
| 3 | `season_multiplier` | 8.25 | Seasonality matters significantly |
| 4 | `discount_per_day` | 6.54 | Discount timing effectiveness |
| 5 | `discount_expiry_interaction` | 5.90 | Combined effect is important |
| 6 | `urgency_score` | 4.53 | Urgency influences decisions |
| 7 | `day_of_week` | 4.42 | Day matters (weekend effect) |
| 8 | `price_discount_ratio` | 4.27 | Relative discount impact |
| 9 | `days_to_expiry` | 4.20 | Expiry urgency effect |
| 10 | `inventory_level` | 3.96 | Scarcity effect present |

### Key Insights

1. **Deep discounts (≥30%) are by far the most important factor** (6× more than next feature)
2. **Discount-related features dominate**: 5 of top 10 are discount-based
3. **Temporal factors matter**: Season, day of week, expiry all contribute
4. **Engineered features work**: Interaction terms show up in top 10

## Model Parameters

```python
{
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 1,
    'seed': 42
}
```

**Training Details:**
- Boosting rounds: 100 (early stopped at round 10)
- Train/Val/Test split: 70/10/20
- Training time: 0.06 seconds
- Best validation AUC: 0.6695

## Usage

### 1. Load Model

```python
import xgboost as xgb
import pandas as pd
import joblib

# Load model
model = xgb.Booster()
model.load_model('models/xgb_recommend.json')

# Load feature names and encoders
with open('models/feature_names.json', 'r') as f:
    feature_names = json.load(f)

label_encoders = joblib.load('models/label_encoders.pkl')
```

### 2. Prepare Input Data

```python
def prepare_input(data: dict) -> pd.DataFrame:
    """Prepare single prediction input."""
    
    # Engineer features
    df = pd.DataFrame([data])
    
    # Urgency score
    df['urgency_score'] = (
        (1 / (df['days_to_expiry'] + 1)) * 10 +
        (1 / (df['inventory_level'] + 1)) * 100
    )
    
    # Price tier
    if df['base_price'].iloc[0] <= 5:
        df['price_tier'] = 'low'
    elif df['base_price'].iloc[0] <= 15:
        df['price_tier'] = 'medium'
    else:
        df['price_tier'] = 'high'
    
    # Other engineered features
    df['discount_per_day'] = df['discount_pct'] / (df['days_to_expiry'] + 1)
    df['inventory_risk'] = ((df['inventory_level'] < 20) & (df['days_to_expiry'] < 7)).astype(int)
    df['high_urgency'] = (df['days_to_expiry'] <= 3).astype(int)
    df['deep_discount'] = (df['discount_pct'] >= 30).astype(int)
    df['discount_expiry_interaction'] = df['discount_pct'] * (1 / (df['days_to_expiry'] + 1))
    df['price_discount_ratio'] = df['discount_pct'] / (df['base_price'] + 1)
    
    # Encode categorical
    df['category_encoded'] = label_encoders['category'].transform(df['category'])
    df['price_tier_encoded'] = label_encoders['price_tier'].transform(df['price_tier'])
    
    return df[feature_names]
```

### 3. Make Predictions

```python
# Example input
product_data = {
    'base_price': 12.99,
    'discount_pct': 25.0,
    'days_to_expiry': 3,
    'inventory_level': 8,
    'day_of_week': 5,  # Saturday
    'month': 11,
    'is_weekend': 1,
    'is_summer': 0,
    'is_winter': 0,
    'is_holiday_season': 1,
    'season_multiplier': 1.0,
    'category': 'Seafood'
}

# Prepare features
X = prepare_input(product_data)

# Predict
dmatrix = xgb.DMatrix(X)
probability = model.predict(dmatrix)[0]

print(f"Purchase Probability: {probability:.2%}")
# Output: Purchase Probability: 68.5%
```

### 4. Batch Predictions

```python
# Load CSV
df = pd.read_csv('new_products.csv')

# Engineer features (same as training)
# ... (feature engineering code)

# Predict
dmatrix = xgb.DMatrix(df[feature_names])
probabilities = model.predict(dmatrix)

df['purchase_probability'] = probabilities
df['predicted_sold'] = (probabilities >= 0.5).astype(int)
```

## Files

```
models/
├── xgb_recommend.json      # XGBoost model (128KB)
├── feature_names.json      # Feature list
├── label_encoders.pkl      # Category encoders
├── metrics.json            # Performance metrics
├── model_info.json         # Model metadata
└── README.md              # This file
```

## Limitations & Considerations

### Current Limitations

1. **Moderate Accuracy (65%)**: Model has room for improvement
   - Consider collecting more training data
   - Try hyperparameter tuning
   - Experiment with different algorithms (LightGBM, CatBoost)

2. **Low Recall (39%)**: Misses many actual purchases
   - May need to adjust decision threshold
   - Consider business impact of false negatives
   - Use probability scores instead of binary predictions

3. **Synthetic Data**: Trained on simulated data
   - Performance may differ on real-world data
   - Retrain with actual purchase logs when available

4. **Static Model**: No online learning
   - Requires retraining for updates
   - Consider A/B testing new models

### When to Use

✅ **Good for:**
- Initial discount recommendations
- A/B testing baseline
- Understanding feature importance
- Bulk predictions on inventory

❌ **Not ideal for:**
- Critical business decisions (moderate accuracy)
- Real-time optimization (low recall)
- Personalized recommendations (no user features)

## Improvement Roadmap

### Short-term (Week 4)
- [x] Train baseline model (65% accuracy)
- [ ] Hyperparameter tuning (GridSearch)
- [ ] Adjust decision threshold for better recall
- [ ] Add model explainability (SHAP values)

### Medium-term (Week 5-6)
- [ ] Collect real purchase data
- [ ] Retrain with actual data
- [ ] Add user behavior features
- [ ] Implement uplift modeling
- [ ] A/B test in production

### Long-term (Month 2+)
- [ ] Time series forecasting
- [ ] Personalization engine
- [ ] Multi-armed bandit optimization
- [ ] Deep learning models
- [ ] Real-time learning pipeline

## Model Retraining

```bash
# Retrain with new data
python3 scripts/train_model.py data/new_purchases.csv

# With hyperparameter tuning
python3 scripts/train_model.py data/new_purchases.csv --tune

# Custom settings
python3 scripts/train_model.py data/new_purchases.csv \
  --num-rounds 200 \
  --test-size 0.15 \
  --val-size 0.15
```

## Support

For questions or issues:
1. Review training logs in console output
2. Check `models/metrics.json` for detailed performance
3. Examine feature importance for insights
4. See `scripts/train_model.py` for implementation

---

**Model Version**: 1.0  
**Last Updated**: 2025-11-15  
**Status**: Production Ready (Baseline)
