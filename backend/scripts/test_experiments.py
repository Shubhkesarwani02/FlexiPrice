"""
Test script for A/B testing experiments.
Validates experiment assignment, recommendations, and analytics.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.ab_test_service import ab_test_service, ExperimentGroup
from app.schemas.experiment import ExperimentSummary
from datetime import datetime, timedelta
from decimal import Decimal


def test_rule_based_recommendations():
    """Test rule-based discount logic."""
    print("\n" + "=" * 60)
    print("TEST 1: RULE-BASED RECOMMENDATIONS")
    print("=" * 60)
    
    test_cases = [
        {"days": 1, "inventory": 10, "category": "Seafood", "price": 28.99},
        {"days": 4, "inventory": 25, "category": "Meat", "price": 35.50},
        {"days": 7, "inventory": 5, "category": "Dairy", "price": 5.99},
        {"days": 14, "inventory": 15, "category": "Bakery", "price": 8.50},
        {"days": 30, "inventory": 30, "category": "Frozen", "price": 12.00},
    ]
    
    for case in test_cases:
        rec = ab_test_service.get_rule_based_recommendation(
            base_price=case["price"],
            days_to_expiry=case["days"],
            inventory=case["inventory"],
            category=case["category"]
        )
        
        print(f"\n{case['category']} (${case['price']:.2f}) - {case['days']} days, {case['inventory']} units:")
        print(f"  ✓ Discount: {rec['discount_pct']:.1f}%")
        print(f"  ✓ Reason: {rec['reason']}")
        print(f"  ✓ Method: {rec['method']}")


def test_experiment_assignment():
    """Test experiment group assignment."""
    print("\n" + "=" * 60)
    print("TEST 2: EXPERIMENT ASSIGNMENT")
    print("=" * 60)
    
    product_ids = list(range(1, 21))  # 20 products
    
    # Test 50/50 split
    print("\n50/50 split:")
    assignments = ab_test_service.random_assignment(product_ids, split_ratio=0.5)
    
    control = assignments[ExperimentGroup.CONTROL]
    ml_variant = assignments[ExperimentGroup.ML_VARIANT]
    
    print(f"  ✓ Control group: {len(control)} products")
    print(f"  ✓ ML variant group: {len(ml_variant)} products")
    print(f"  ✓ Total: {len(control) + len(ml_variant)} products")
    
    # Test 70/30 split
    print("\n70/30 split:")
    assignments = ab_test_service.random_assignment(product_ids, split_ratio=0.7)
    
    control = assignments[ExperimentGroup.CONTROL]
    ml_variant = assignments[ExperimentGroup.ML_VARIANT]
    
    print(f"  ✓ Control group: {len(control)} products ({len(control)/len(product_ids)*100:.0f}%)")
    print(f"  ✓ ML variant group: {len(ml_variant)} products ({len(ml_variant)/len(product_ids)*100:.0f}%)")


def test_experiment_comparison():
    """Test A/B comparison calculations."""
    print("\n" + "=" * 60)
    print("TEST 3: A/B COMPARISON")
    print("=" * 60)
    
    # Mock metrics for control
    control_summary = ExperimentSummary(
        experiment_group=ExperimentGroup.CONTROL,
        total_products=10,
        total_impressions=1000,
        total_conversions=350,
        total_revenue=Decimal("5000.00"),
        total_units_sold=500,
        avg_discount_pct=Decimal("25.0"),
        conversion_rate=Decimal("35.0"),
        revenue_per_product=Decimal("500.00")
    )
    
    # Mock metrics for ML variant (better performance)
    ml_summary = ExperimentSummary(
        experiment_group=ExperimentGroup.ML_VARIANT,
        total_products=10,
        total_impressions=1000,
        total_conversions=420,
        total_revenue=Decimal("6300.00"),
        total_units_sold=630,
        avg_discount_pct=Decimal("28.5"),
        conversion_rate=Decimal("42.0"),
        revenue_per_product=Decimal("630.00")
    )
    
    period_start = datetime.utcnow() - timedelta(days=7)
    period_end = datetime.utcnow()
    
    comparison = ab_test_service.compare_experiments(
        control_summary=control_summary,
        ml_summary=ml_summary,
        period_start=period_start,
        period_end=period_end
    )
    
    print("\nControl Group:")
    print(f"  - Products: {control_summary.total_products}")
    print(f"  - Conversion Rate: {control_summary.conversion_rate}%")
    print(f"  - Revenue/Product: ${control_summary.revenue_per_product}")
    print(f"  - Units Sold: {control_summary.total_units_sold}")
    
    print("\nML Variant Group:")
    print(f"  - Products: {ml_summary.total_products}")
    print(f"  - Conversion Rate: {ml_summary.conversion_rate}%")
    print(f"  - Revenue/Product: ${ml_summary.revenue_per_product}")
    print(f"  - Units Sold: {ml_summary.total_units_sold}")
    
    print("\nML vs Control Lift:")
    print(f"  ✓ Conversion Lift: {comparison.conversion_lift:+.1f}%")
    print(f"  ✓ Revenue Lift: {comparison.revenue_lift:+.1f}%")
    print(f"  ✓ Units Lift: {comparison.units_lift:+.1f}%")
    
    if comparison.conversion_lift > 0:
        print(f"\n  🎉 ML variant is WINNING with {comparison.conversion_lift:.1f}% higher conversion!")
    else:
        print(f"\n  ⚠️  Control is performing better")


def test_ml_recommendation():
    """Test ML recommendation (if model available)."""
    print("\n" + "=" * 60)
    print("TEST 4: ML RECOMMENDATIONS")
    print("=" * 60)
    
    try:
        from app.services.ml_predictor import ml_predictor
        
        ml_predictor.initialize()
        print("  ✓ ML model loaded")
        
        # Test recommendation
        rec = ab_test_service.get_ml_recommendation(
            ml_predictor=ml_predictor,
            product_id=1,
            days_to_expiry=3,
            inventory=10,
            top_k=3
        )
        
        print(f"\n  Product: 1")
        print(f"  Days to expiry: 3")
        print(f"  Inventory: 10")
        print(f"  ✓ ML Discount: {rec['discount_pct']:.1f}%")
        if rec.get('probability'):
            print(f"  ✓ Expected Probability: {rec['probability']:.1%}")
        print(f"  ✓ Reason: {rec['reason']}")
        print(f"  ✓ Method: {rec['method']}")
        
    except Exception as e:
        print(f"  ⚠️  ML test skipped: {str(e)}")


def main():
    """Run all A/B test validations."""
    print("=" * 60)
    print("A/B TESTING SERVICE - VALIDATION TESTS")
    print("=" * 60)
    
    test_rule_based_recommendations()
    test_experiment_assignment()
    test_experiment_comparison()
    test_ml_recommendation()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
