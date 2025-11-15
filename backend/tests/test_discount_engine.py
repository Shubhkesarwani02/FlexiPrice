"""
Test script for the Discount Engine

Run this to test discount calculations without database dependencies.
"""

from decimal import Decimal
from app.core.discount_engine import DiscountEngine, compute_batch_price


def test_discount_engine():
    """Test the discount engine with various scenarios."""
    
    print("=" * 60)
    print("🧪 DISCOUNT ENGINE TEST SUITE")
    print("=" * 60)
    print()
    
    engine = DiscountEngine()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Critical Expiry - 1 Day",
            "base_price": Decimal("10.00"),
            "days_to_expiry": 1,
            "quantity": 50,
            "category": "dairy",
        },
        {
            "name": "High Urgency - 5 Days",
            "base_price": Decimal("15.99"),
            "days_to_expiry": 5,
            "quantity": 30,
            "category": None,
        },
        {
            "name": "Medium Urgency - 10 Days",
            "base_price": Decimal("25.00"),
            "days_to_expiry": 10,
            "quantity": 75,
            "category": "produce",
        },
        {
            "name": "Low Urgency - 25 Days",
            "base_price": Decimal("8.50"),
            "days_to_expiry": 25,
            "quantity": 40,
            "category": None,
        },
        {
            "name": "Overstocked - 20 Days, 150 Units",
            "base_price": Decimal("12.00"),
            "days_to_expiry": 20,
            "quantity": 150,
            "category": None,
        },
        {
            "name": "No Discount - 60 Days",
            "base_price": Decimal("20.00"),
            "days_to_expiry": 60,
            "quantity": 25,
            "category": None,
        },
        {
            "name": "Bakery Same Day",
            "base_price": Decimal("5.99"),
            "days_to_expiry": 0,
            "quantity": 20,
            "category": "bakery",
        },
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Test {i}: {scenario['name']}")
        print("-" * 60)
        
        computed_price, discount_pct, rule_name = engine.compute_batch_price(
            base_price=scenario["base_price"],
            days_to_expiry=scenario["days_to_expiry"],
            quantity=scenario["quantity"],
            category=scenario["category"],
        )
        
        savings = scenario["base_price"] - computed_price
        
        print(f"  Base Price:       ${scenario['base_price']}")
        print(f"  Days to Expiry:   {scenario['days_to_expiry']}")
        print(f"  Quantity:         {scenario['quantity']}")
        print(f"  Category:         {scenario['category'] or 'None'}")
        print(f"  ")
        print(f"  ✨ Rule Applied:   {rule_name}")
        print(f"  💰 Computed Price: ${computed_price}")
        print(f"  📉 Discount:       {discount_pct}%")
        print(f"  💵 Savings:        ${savings}")
        print()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


def test_direct_function():
    """Test the convenience function."""
    print("\n🔧 Testing direct compute_batch_price function...")
    print()
    
    price, discount, rule = compute_batch_price(
        base_price=Decimal("100.00"),
        days_to_expiry=3,
        quantity=200,
        category="dairy",
    )
    
    print(f"Result: ${price} with {discount}% discount ({rule})")
    print()


if __name__ == "__main__":
    test_discount_engine()
    test_direct_function()
