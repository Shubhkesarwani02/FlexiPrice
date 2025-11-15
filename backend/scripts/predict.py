"""
Simple script to test XGBoost model predictions.

Usage:
    python3 scripts/predict.py
"""

import json
import xgboost as xgb
import pandas as pd
import joblib


def load_model_artifacts():
    """Load model and associated artifacts."""
    print("Loading model artifacts...")
    
    model = xgb.Booster()
    model.load_model('models/xgb_recommend.json')
    
    with open('models/feature_names.json', 'r') as f:
        feature_names = json.load(f)
    
    label_encoders = joblib.load('models/label_encoders.pkl')
    
    print(f"✓ Model loaded")
    print(f"✓ Features: {len(feature_names)}")
    
    return model, feature_names, label_encoders


def engineer_features(data: dict) -> dict:
    """Add engineered features to input data."""
    
    # Urgency score
    data['urgency_score'] = (
        (1 / (data['days_to_expiry'] + 1)) * 10 +
        (1 / (data['inventory_level'] + 1)) * 100
    )
    
    # Price tier
    if data['base_price'] <= 5:
        data['price_tier'] = 'low'
    elif data['base_price'] <= 15:
        data['price_tier'] = 'medium'
    else:
        data['price_tier'] = 'high'
    
    # Discount per day
    data['discount_per_day'] = data['discount_pct'] / (data['days_to_expiry'] + 1)
    
    # Inventory risk
    data['inventory_risk'] = int(data['inventory_level'] < 20 and data['days_to_expiry'] < 7)
    
    # High urgency
    data['high_urgency'] = int(data['days_to_expiry'] <= 3)
    
    # Deep discount
    data['deep_discount'] = int(data['discount_pct'] >= 30)
    
    # Discount expiry interaction
    data['discount_expiry_interaction'] = data['discount_pct'] * (1 / (data['days_to_expiry'] + 1))
    
    # Price discount ratio
    data['price_discount_ratio'] = data['discount_pct'] / (data['base_price'] + 1)
    
    return data


def prepare_input(data: dict, feature_names: list, label_encoders: dict) -> pd.DataFrame:
    """Prepare input for prediction."""
    
    # Engineer features
    data = engineer_features(data)
    
    # Encode categorical
    data['category_encoded'] = label_encoders['category'].transform([data['category']])[0]
    data['price_tier_encoded'] = label_encoders['price_tier'].transform([data['price_tier']])[0]
    
    # Create DataFrame with correct feature order
    df = pd.DataFrame([data])
    return df[feature_names]


def predict(model, X: pd.DataFrame) -> float:
    """Make prediction."""
    dmatrix = xgb.DMatrix(X)
    probability = model.predict(dmatrix)[0]
    return probability


def main():
    print("\n" + "="*70)
    print("XGBOOST PURCHASE PREDICTION - TEST")
    print("="*70 + "\n")
    
    # Load model
    model, feature_names, label_encoders = load_model_artifacts()
    
    # Test cases
    test_cases = [
        {
            "name": "High Discount Seafood - Weekend",
            "data": {
                'base_price': 28.99,
                'discount_pct': 35.0,
                'days_to_expiry': 2,
                'inventory_level': 5,
                'day_of_week': 6,  # Sunday
                'month': 7,
                'is_weekend': 1,
                'is_summer': 1,
                'is_winter': 0,
                'is_holiday_season': 0,
                'season_multiplier': 1.3,
                'category': 'Seafood'
            }
        },
        {
            "name": "Low Discount Snacks - Weekday",
            "data": {
                'base_price': 4.99,
                'discount_pct': 10.0,
                'days_to_expiry': 45,
                'inventory_level': 120,
                'day_of_week': 2,  # Wednesday
                'month': 3,
                'is_weekend': 0,
                'is_summer': 0,
                'is_winter': 0,
                'is_holiday_season': 0,
                'season_multiplier': 1.0,
                'category': 'Snacks'
            }
        },
        {
            "name": "Moderate Discount Dairy - Urgent",
            "data": {
                'base_price': 6.50,
                'discount_pct': 25.0,
                'days_to_expiry': 3,
                'inventory_level': 15,
                'day_of_week': 5,  # Saturday
                'month': 11,
                'is_weekend': 1,
                'is_summer': 0,
                'is_winter': 0,
                'is_holiday_season': 1,
                'season_multiplier': 1.0,
                'category': 'Dairy'
            }
        },
        {
            "name": "High Price Meat - Deep Discount",
            "data": {
                'base_price': 35.00,
                'discount_pct': 40.0,
                'days_to_expiry': 4,
                'inventory_level': 8,
                'day_of_week': 4,  # Friday
                'month': 12,
                'is_weekend': 0,
                'is_summer': 0,
                'is_winter': 1,
                'is_holiday_season': 1,
                'season_multiplier': 0.9,
                'category': 'Meat'
            }
        }
    ]
    
    print("\nTest Predictions:\n")
    print("-" * 70)
    
    for i, test in enumerate(test_cases, 1):
        data = test['data']
        X = prepare_input(data, feature_names, label_encoders)
        probability = predict(model, X)
        
        print(f"\n{i}. {test['name']}")
        print(f"   Product: {data['category']}, ${data['base_price']:.2f}")
        print(f"   Discount: {data['discount_pct']:.1f}%, Expiry: {data['days_to_expiry']} days")
        print(f"   Inventory: {data['inventory_level']} units")
        print(f"   → Purchase Probability: {probability:.1%}")
        print(f"   → Prediction: {'WILL BUY' if probability >= 0.5 else 'WILL NOT BUY'}")
    
    print("\n" + "-" * 70)
    
    # Interactive mode
    print("\n\nInteractive Prediction (press Ctrl+C to exit)\n")
    
    try:
        while True:
            print("\nEnter product details:")
            
            data = {
                'category': input("  Category (Dairy/Bakery/Meat/Seafood/Produce/Frozen/Beverages/Snacks): ").strip(),
                'base_price': float(input("  Base price ($): ")),
                'discount_pct': float(input("  Discount (%): ")),
                'days_to_expiry': int(input("  Days to expiry: ")),
                'inventory_level': int(input("  Inventory level: ")),
                'day_of_week': int(input("  Day of week (0=Mon, 6=Sun): ")),
                'month': int(input("  Month (1-12): ")),
            }
            
            # Set flags based on inputs
            data['is_weekend'] = 1 if data['day_of_week'] >= 5 else 0
            data['is_summer'] = 1 if data['month'] in [6, 7, 8] else 0
            data['is_winter'] = 1 if data['month'] in [12, 1, 2] else 0
            data['is_holiday_season'] = 1 if data['month'] in [11, 12] else 0
            data['season_multiplier'] = 1.0  # Simplified
            
            X = prepare_input(data, feature_names, label_encoders)
            probability = predict(model, X)
            
            print(f"\n  → Purchase Probability: {probability:.1%}")
            print(f"  → Prediction: {'WILL BUY ✓' if probability >= 0.5 else 'WILL NOT BUY ✗'}")
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
