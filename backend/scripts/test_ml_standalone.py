"""
Standalone ML Service Test
Tests ML functionality without database dependencies.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

try:
    import xgboost as xgb
    import pandas as pd
    import joblib
    
    print("\n" + "="*70)
    print("ML API WRAPPER TEST - STANDALONE")
    print("="*70 + "\n")
    
    # Test 1: Load Model
    print("1. Loading Model...")
    model_dir = backend_path / "models"
    model_path = model_dir / "xgb_recommend.json"
    
    if not model_path.exists():
        print(f"✗ Model not found at {model_path}")
        print("  Run: python3 scripts/train_model.py data/synthetic_purchases.csv")
        sys.exit(1)
    
    model = xgb.Booster()
    model.load_model(str(model_path))
    print(f"✓ Model loaded from {model_path}")
    
    # Load artifacts
    with open(model_dir / "feature_names.json", 'r') as f:
        feature_names = json.load(f)
    label_encoders = joblib.load(model_dir / "label_encoders.pkl")
    with open(model_dir / "model_info.json", 'r') as f:
        model_info = json.load(f)
    
    print(f"✓ Features: {len(feature_names)}")
    print(f"✓ Model: {model_info['model_type']}")
    print(f"✓ Accuracy: {model_info['performance']['accuracy']:.1%}\n")
    
    # Test 2: Single Prediction
    print("2. Testing Single Prediction...")
    
    def engineer_features(data):
        """Add engineered features."""
        features = data.copy()
        features['urgency_score'] = (
            (1 / (features['days_to_expiry'] + 1)) * 10 +
            (1 / (features['inventory_level'] + 1)) * 100
        )
        if features['base_price'] <= 5:
            features['price_tier'] = 'low'
        elif features['base_price'] <= 15:
            features['price_tier'] = 'medium'
        else:
            features['price_tier'] = 'high'
        features['discount_per_day'] = features['discount_pct'] / (features['days_to_expiry'] + 1)
        features['inventory_risk'] = int(features['inventory_level'] < 20 and features['days_to_expiry'] < 7)
        features['high_urgency'] = int(features['days_to_expiry'] <= 3)
        features['deep_discount'] = int(features['discount_pct'] >= 30)
        features['discount_expiry_interaction'] = features['discount_pct'] * (1 / (features['days_to_expiry'] + 1))
        features['price_discount_ratio'] = features['discount_pct'] / (features['base_price'] + 1)
        return features
    
    test_data = {
        'base_price': 28.99,
        'category': 'Seafood',
        'discount_pct': 35.0,
        'days_to_expiry': 2,
        'inventory_level': 5,
        'day_of_week': 6,
        'month': 11,
        'is_weekend': 1,
        'is_summer': 0,
        'is_winter': 0,
        'is_holiday_season': 1,
        'season_multiplier': 0.8
    }
    
    features = engineer_features(test_data)
    features['category_encoded'] = label_encoders['category'].transform([features['category']])[0]
    features['price_tier_encoded'] = label_encoders['price_tier'].transform([features['price_tier']])[0]
    
    df = pd.DataFrame([features])
    X = df[feature_names]
    dmatrix = xgb.DMatrix(X)
    probability = float(model.predict(dmatrix)[0])
    
    print(f"   Input: Seafood $28.99, 35% discount, 2 days")
    print(f"   → Probability: {probability:.1%}")
    print(f"   → Prediction: {'WILL BUY ✓' if probability >= 0.5 else 'WILL NOT BUY ✗'}\n")
    
    # Test 3: Discount Recommendations
    print("3. Testing Discount Recommendations...")
    print("   Product: Seafood $28.99, 3 days to expiry, 10 units\n")
    
    # Test different discount levels
    base_product = {
        'base_price': 28.99,
        'category': 'Seafood',
        'days_to_expiry': 3,
        'inventory_level': 10,
        'day_of_week': datetime.now().weekday(),
        'month': datetime.now().month,
        'is_weekend': 1 if datetime.now().weekday() >= 5 else 0,
        'is_summer': 1 if datetime.now().month in [6, 7, 8] else 0,
        'is_winter': 1 if datetime.now().month in [12, 1, 2] else 0,
        'is_holiday_season': 1 if datetime.now().month in [11, 12] else 0,
        'season_multiplier': 0.8
    }
    
    # Baseline (no discount)
    baseline = base_product.copy()
    baseline['discount_pct'] = 0.0
    baseline_features = engineer_features(baseline)
    baseline_features['category_encoded'] = label_encoders['category'].transform([baseline_features['category']])[0]
    baseline_features['price_tier_encoded'] = label_encoders['price_tier'].transform([baseline_features['price_tier']])[0]
    baseline_df = pd.DataFrame([baseline_features])[feature_names]
    baseline_prob = float(model.predict(xgb.DMatrix(baseline_df))[0])
    
    # Test discounts
    discount_levels = [10, 20, 30, 40, 50]
    recommendations = []
    
    for discount in discount_levels:
        test = base_product.copy()
        test['discount_pct'] = float(discount)
        test_features = engineer_features(test)
        test_features['category_encoded'] = label_encoders['category'].transform([test_features['category']])[0]
        test_features['price_tier_encoded'] = label_encoders['price_tier'].transform([test_features['price_tier']])[0]
        test_df = pd.DataFrame([test_features])[feature_names]
        prob = float(model.predict(xgb.DMatrix(test_df))[0])
        
        uplift = prob - baseline_prob
        uplift_pct = (uplift / baseline_prob * 100) if baseline_prob > 0 else 0
        discounted_price = base_product['base_price'] * (1 - discount / 100)
        expected_revenue = discounted_price * prob * base_product['inventory_level']
        
        recommendations.append({
            'discount_pct': discount,
            'purchase_probability': prob,
            'uplift': uplift,
            'uplift_pct': uplift_pct,
            'expected_revenue': expected_revenue,
            'discounted_price': discounted_price,
            'confidence': 'high' if prob >= 0.7 else 'medium' if prob >= 0.5 else 'low'
        })
    
    # Sort and display top 3
    recommendations.sort(key=lambda x: x['purchase_probability'], reverse=True)
    
    print("   " + "-"*68)
    print(f"   {'Discount':<10} {'Prob':<8} {'Uplift':<12} {'Revenue':<12} {'Price':<10} {'Conf'}")
    print("   " + "-"*68)
    
    for rec in recommendations[:3]:
        print(f"   {rec['discount_pct']:.0f}%{' '*6} "
              f"{rec['purchase_probability']:.1%}{' '*3} "
              f"{rec['uplift']:+.4f} ({rec['uplift_pct']:+.1f}%){' '*1} "
              f"${rec['expected_revenue']:.2f}{' '*3} "
              f"${rec['discounted_price']:.2f}{' '*3} "
              f"{rec['confidence']}")
    
    print("   " + "-"*68)
    print(f"   Baseline (0%): {baseline_prob:.1%} probability\n")
    
    # Test 4: API Response Format
    print("4. Sample API Response:")
    print("   GET /api/v1/admin/ml/recommend?product_id=SEA-123&days_to_expiry=3&inventory=10\n")
    
    api_response = {
        "recommendations": [
            {
                "product_id": "SEA-123",
                "category": "Seafood",
                "base_price": 28.99,
                "days_to_expiry": 3,
                "inventory_level": 10,
                "discount_pct": recommendations[0]['discount_pct'],
                "discounted_price": recommendations[0]['discounted_price'],
                "purchase_probability": recommendations[0]['purchase_probability'],
                "baseline_probability": baseline_prob,
                "uplift": recommendations[0]['uplift'],
                "uplift_pct": recommendations[0]['uplift_pct'],
                "expected_revenue": recommendations[0]['expected_revenue'],
                "confidence": recommendations[0]['confidence']
            }
        ],
        "model_info": {
            "model_type": model_info['model_type'],
            "num_features": model_info['num_features'],
            "training_date": model_info['training_date'],
            "performance": model_info['performance']
        }
    }
    
    print(json.dumps(api_response, indent=2))
    
    print("\n" + "="*70)
    print("✓ ML API WRAPPER TEST COMPLETE")
    print("="*70)
    print("\nAPI Endpoints Created:")
    print("  GET  /api/v1/admin/ml/recommend - Get discount recommendations")
    print("  POST /api/v1/admin/ml/predict - Predict purchase probability")
    print("  GET  /api/v1/admin/ml/model-info - Get model information")
    print("\nExample cURL:")
    print('  curl "http://localhost:8000/api/v1/admin/ml/recommend?product_id=SEA-123&days_to_expiry=3&inventory=10&top_k=3"')
    print()

except ImportError as e:
    print(f"\n✗ Import error: {e}")
    print("  Install dependencies: pip3 install xgboost scikit-learn pandas")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
