"""
Test ML Predictor Service
Tests the ML predictor without requiring full API server.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock prisma for testing
class MockProduct:
    def __init__(self, sku, name, category, basePrice):
        self.sku = sku
        self.name = name
        self.category = category
        self.basePrice = basePrice

class MockPrisma:
    class product:
        @staticmethod
        async def findUnique(where):
            # Return mock products
            mock_products = {
                "SEA-00123": MockProduct("SEA-00123", "Fresh Salmon", "Seafood", 28.99),
                "DAI-00456": MockProduct("DAI-00456", "Organic Milk", "Dairy", 6.50),
                "MEA-00789": MockProduct("MEA-00789", "Prime Beef", "Meat", 35.00),
                "SNA-00111": MockProduct("SNA-00111", "Potato Chips", "Snacks", 4.99),
            }
            return mock_products.get(where.get("sku"))

# Patch prisma
import app.core.database as db
db.prisma = MockPrisma()

from app.services.ml_predictor import ml_predictor


async def test_ml_predictor():
    """Test ML predictor functionality."""
    print("\n" + "="*70)
    print("ML PREDICTOR SERVICE TEST")
    print("="*70 + "\n")
    
    # Initialize
    print("1. Initializing ML predictor...")
    success = ml_predictor.initialize()
    
    if not success:
        print("✗ Failed to initialize ML predictor")
        print("  Make sure the model is trained and saved in backend/models/")
        return
    
    print("✓ ML predictor initialized successfully\n")
    
    # Get model info
    print("2. Model Information:")
    info = ml_predictor.get_model_info()
    print(f"   Model type: {info.get('model_type')}")
    print(f"   Features: {info.get('num_features')}")
    print(f"   Training date: {info.get('training_date')}")
    print(f"   Accuracy: {info.get('performance', {}).get('accuracy', 'N/A')}")
    print(f"   ROC-AUC: {info.get('performance', {}).get('roc_auc', 'N/A')}\n")
    
    # Test single prediction
    print("3. Testing Single Prediction:")
    test_data = {
        'base_price': 28.99,
        'category': 'Seafood',
        'discount_pct': 35.0,
        'days_to_expiry': 2,
        'inventory_level': 5,
        'day_of_week': 6,  # Sunday
        'month': 11,
        'is_weekend': 1,
        'is_summer': 0,
        'is_winter': 0,
        'is_holiday_season': 1,
        'season_multiplier': 0.8
    }
    
    probability = ml_predictor.predict_probability(test_data)
    print(f"   Input: Seafood $28.99, 35% discount, 2 days to expiry")
    print(f"   → Purchase Probability: {probability:.1%}")
    print(f"   → Prediction: {'WILL BUY ✓' if probability >= 0.5 else 'WILL NOT BUY ✗'}\n")
    
    # Test discount recommendations
    print("4. Testing Discount Recommendations:")
    print("   Product: SEA-00123 (Fresh Salmon)")
    print("   Days to expiry: 3, Inventory: 10\n")
    
    recommendations = await ml_predictor.recommend_discounts(
        product_id="SEA-00123",
        days_to_expiry=3,
        inventory_level=10,
        top_k=3,
        discount_range=(10.0, 50.0),
        discount_step=10.0
    )
    
    print("   Top 3 Recommendations:")
    print("   " + "-"*66)
    print(f"   {'Discount':<12} {'Prob':<8} {'Uplift':<10} {'Revenue':<12} {'Confidence':<12}")
    print("   " + "-"*66)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {rec['discount_pct']:.1f}%{' '*7} "
              f"{rec['purchase_probability']:.1%}{' '*3} "
              f"+{rec['uplift_pct']:.1f}%{' '*5} "
              f"${rec['expected_revenue']:.2f}{' '*4} "
              f"{rec['confidence']}")
    
    print("   " + "-"*66 + "\n")
    
    # Test multiple products
    print("5. Testing Multiple Products:\n")
    
    test_cases = [
        ("DAI-00456", "Organic Milk", 3, 15),
        ("MEA-00789", "Prime Beef", 4, 8),
        ("SNA-00111", "Potato Chips", 45, 120),
    ]
    
    for product_id, name, days, inventory in test_cases:
        recs = await ml_predictor.recommend_discounts(
            product_id=product_id,
            days_to_expiry=days,
            inventory_level=inventory,
            top_k=1
        )
        
        if recs:
            best = recs[0]
            print(f"   {name:20s} ({days:2d} days, {inventory:3d} units)")
            print(f"   → Best: {best['discount_pct']:.0f}% discount → {best['purchase_probability']:.1%} probability")
            print()
    
    print("="*70)
    print("TEST COMPLETE ✓")
    print("="*70 + "\n")
    
    # Return sample API response
    print("6. Sample API Response Format:\n")
    sample_response = {
        "recommendations": recommendations[:1],
        "model_info": info
    }
    print(json.dumps(sample_response, indent=2))
    print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ml_predictor())
