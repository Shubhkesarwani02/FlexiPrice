"""
End-to-end test for A/B experiment system.
Tests: assignment, recommendations, analytics.
"""

import sys
from pathlib import Path
import requests
import json

# Test configuration
API_BASE = "http://localhost:8000/api/v1"


def test_experiment_status():
    """Test experiment status endpoint."""
    print("\n" + "=" * 60)
    print("TEST 1: EXPERIMENT STATUS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/admin/experiments/status")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Total Products: {data['total_products']}")
        print(f"✓ Assigned: {data['assigned_products']}")
        print(f"✓ Control: {data['control_count']}")
        print(f"✓ ML Variant: {data['ml_variant_count']}")
        print(f"✓ Experiment Active: {data['experiment_active']}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False


def test_random_assignment():
    """Test random experiment assignment."""
    print("\n" + "=" * 60)
    print("TEST 2: RANDOM ASSIGNMENT")
    print("=" * 60)
    
    try:
        response = requests.post(f"{API_BASE}/admin/experiments/assign/random?split_ratio=0.5")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Message: {data['message']}")
        print(f"✓ Control Count: {data['control_count']}")
        print(f"✓ ML Variant Count: {data['ml_variant_count']}")
        print(f"✓ Total Assigned: {len(data['assignments'])}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False


def test_recommendations():
    """Test getting recommendations for both groups."""
    print("\n" + "=" * 60)
    print("TEST 3: RECOMMENDATIONS")
    print("=" * 60)
    
    test_cases = [
        {"productId": 1, "daysToExpiry": 3, "inventory": 10},
        {"productId": 5, "daysToExpiry": 7, "inventory": 25},
        {"productId": 10, "daysToExpiry": 1, "inventory": 5},
    ]
    
    success_count = 0
    
    for case in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/admin/experiments/recommend",
                json=case
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"\nProduct {case['productId']} ({case['daysToExpiry']} days, {case['inventory']} units):")
            print(f"  ✓ Group: {data['experimentGroup']}")
            print(f"  ✓ Discount: {data['recommendedDiscountPct']}%")
            print(f"  ✓ Method: {data['method']}")
            print(f"  ✓ Reason: {data['reason']}")
            
            success_count += 1
        except Exception as e:
            print(f"\n  ✗ Product {case['productId']} failed: {str(e)}")
    
    print(f"\n✓ {success_count}/{len(test_cases)} recommendations successful")
    return success_count == len(test_cases)


def test_analytics_comparison():
    """Test A/B analytics comparison."""
    print("\n" + "=" * 60)
    print("TEST 4: ANALYTICS COMPARISON")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/admin/experiments/analytics/comparison?days=7")
        response.raise_for_status()
        
        data = response.json()
        
        print("\nControl Group:")
        print(f"  - Conversion Rate: {data['control']['conversionRate']:.2f}%")
        print(f"  - Revenue/Product: ${data['control']['revenuePerProduct']:.2f}")
        print(f"  - Units Sold: {data['control']['totalUnitsSold']}")
        
        print("\nML Variant Group:")
        print(f"  - Conversion Rate: {data['mlVariant']['conversionRate']:.2f}%")
        print(f"  - Revenue/Product: ${data['mlVariant']['revenuePerProduct']:.2f}")
        print(f"  - Units Sold: {data['mlVariant']['totalUnitsSold']}")
        
        print("\nLifts:")
        print(f"  ✓ Conversion Lift: {data['conversionLift']:+.2f}%")
        print(f"  ✓ Revenue Lift: {data['revenueLift']:+.2f}%")
        print(f"  ✓ Units Lift: {data['unitsLift']:+.2f}%")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False


def test_winning_variant():
    """Test winning variant determination."""
    print("\n" + "=" * 60)
    print("TEST 5: WINNING VARIANT")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_BASE}/admin/experiments/analytics/winning-variant?days=7&metric=conversion_rate"
        )
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✓ Winner: {data['winner']}")
        print(f"✓ Metric: {data['metric']}")
        print(f"✓ Control Value: {data['controlValue']:.2f}")
        print(f"✓ ML Variant Value: {data['mlVariantValue']:.2f}")
        print(f"✓ Improvement: {data['improvementPct']:+.2f}%")
        print(f"✓ Confidence: {data['confidence']}")
        print(f"✓ Message: {data['message']}")
        print(f"✓ Recommendation: {data['recommendation']}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False


def test_assignments_list():
    """Test listing experiment assignments."""
    print("\n" + "=" * 60)
    print("TEST 6: LIST ASSIGNMENTS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/admin/experiments/assignments")
        response.raise_for_status()
        
        data = response.json()
        
        control_count = sum(1 for p in data if p.get('experimentGroup') == 'CONTROL')
        ml_count = sum(1 for p in data if p.get('experimentGroup') == 'ML_VARIANT')
        unassigned = sum(1 for p in data if not p.get('experimentGroup'))
        
        print(f"✓ Total Products: {len(data)}")
        print(f"✓ Control: {control_count}")
        print(f"✓ ML Variant: {ml_count}")
        print(f"✓ Unassigned: {unassigned}")
        
        # Show first 3
        print("\nSample assignments:")
        for product in data[:3]:
            group = product.get('experimentGroup', 'UNASSIGNED')
            print(f"  - {product['sku']}: {group}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False


def main():
    """Run all A/B experiment tests."""
    print("=" * 60)
    print("A/B EXPERIMENT END-TO-END TESTS")
    print("=" * 60)
    print("\nMake sure backend server is running on http://localhost:8000")
    print("Press Enter to start tests...")
    input()
    
    results = []
    
    # Run tests
    results.append(("Status", test_experiment_status()))
    results.append(("Random Assignment", test_random_assignment()))
    results.append(("Recommendations", test_recommendations()))
    results.append(("Analytics Comparison", test_analytics_comparison()))
    results.append(("Winning Variant", test_winning_variant()))
    results.append(("Assignments List", test_assignments_list()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
