"""
Unit tests for the Discount Engine

Tests the rule evaluation and price computation logic.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.core.discount_engine import DiscountEngine, DiscountRule


class TestDiscountRule:
    """Test DiscountRule evaluation logic."""
    
    def test_simple_days_to_expiry_rule(self):
        """Test rule with simple days_to_expiry condition."""
        rule = DiscountRule(
            name="Test Rule",
            condition={"days_to_expiry": {"lte": 7}},
            discount=0.30,
            priority=1
        )
        
        assert rule.evaluate(days_to_expiry=5, quantity=50) is True
        assert rule.evaluate(days_to_expiry=7, quantity=50) is True
        assert rule.evaluate(days_to_expiry=8, quantity=50) is False
    
    def test_range_days_to_expiry_rule(self):
        """Test rule with range condition."""
        rule = DiscountRule(
            name="Range Rule",
            condition={"days_to_expiry": {"lte": 30, "gt": 7}},
            discount=0.15,
            priority=2
        )
        
        assert rule.evaluate(days_to_expiry=7, quantity=50) is False
        assert rule.evaluate(days_to_expiry=8, quantity=50) is True
        assert rule.evaluate(days_to_expiry=30, quantity=50) is True
        assert rule.evaluate(days_to_expiry=31, quantity=50) is False
    
    def test_quantity_condition(self):
        """Test rule with quantity condition."""
        rule = DiscountRule(
            name="High Inventory",
            condition={"quantity": {"gt": 100}},
            discount=0.20,
            priority=3
        )
        
        assert rule.evaluate(days_to_expiry=20, quantity=100) is False
        assert rule.evaluate(days_to_expiry=20, quantity=101) is True
        assert rule.evaluate(days_to_expiry=20, quantity=200) is True
    
    def test_combined_conditions(self):
        """Test rule with both days and quantity conditions."""
        rule = DiscountRule(
            name="Combined Rule",
            condition={
                "days_to_expiry": {"lte": 30},
                "quantity": {"gt": 100}
            },
            discount=0.25,
            priority=4
        )
        
        assert rule.evaluate(days_to_expiry=20, quantity=150) is True
        assert rule.evaluate(days_to_expiry=35, quantity=150) is False
        assert rule.evaluate(days_to_expiry=20, quantity=50) is False
        assert rule.evaluate(days_to_expiry=35, quantity=50) is False


class TestDiscountEngine:
    """Test DiscountEngine price computation."""
    
    @pytest.fixture
    def engine(self):
        """Create a discount engine instance with test config."""
        # Engine will load from default config
        return DiscountEngine()
    
    def test_critical_expiry_discount(self, engine):
        """Test that critical expiry (<=2 days) gets 60% discount."""
        base_price = Decimal("100.00")
        expiry_date = date.today() + timedelta(days=2)
        
        computed_price, discount_pct, reason = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50
        )
        
        assert discount_pct == Decimal("0.60")
        assert computed_price == Decimal("40.00")
        assert "Critical" in reason or "2 days" in reason.lower()
    
    def test_near_expiry_discount(self, engine):
        """Test that near expiry (3-7 days) gets 30% discount."""
        base_price = Decimal("100.00")
        expiry_date = date.today() + timedelta(days=5)
        
        computed_price, discount_pct, reason = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50
        )
        
        assert discount_pct == Decimal("0.30")
        assert computed_price == Decimal("70.00")
    
    def test_high_inventory_discount(self, engine):
        """Test that high inventory triggers additional discount."""
        base_price = Decimal("100.00")
        expiry_date = date.today() + timedelta(days=20)
        
        # With high inventory (>100)
        computed_price_high, discount_high, reason_high = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=150
        )
        
        # With normal inventory
        computed_price_normal, discount_normal, _ = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50
        )
        
        # High inventory should have more discount
        assert discount_high > discount_normal
        assert computed_price_high < computed_price_normal
    
    def test_price_floor_enforcement(self, engine):
        """Test that computed price respects minimum price floor."""
        base_price = Decimal("100.00")
        expiry_date = date.today() - timedelta(days=1)  # Expired
        
        computed_price, discount_pct, _ = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50
        )
        
        # Price should not go below 20% of base (default floor multiplier)
        min_price = base_price * Decimal("0.20")
        assert computed_price >= min_price
    
    def test_custom_price_floor(self, engine):
        """Test that custom minimum price is respected."""
        base_price = Decimal("100.00")
        expiry_date = date.today() + timedelta(days=2)
        min_price = Decimal("50.00")
        
        computed_price, _, _ = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50,
            min_price=min_price
        )
        
        assert computed_price >= min_price
    
    def test_no_discount_for_far_expiry(self, engine):
        """Test that far expiry dates with normal inventory get minimal discount."""
        base_price = Decimal("100.00")
        expiry_date = date.today() + timedelta(days=100)
        
        computed_price, discount_pct, _ = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50
        )
        
        # Should have little to no discount
        assert discount_pct <= Decimal("0.10")
        assert computed_price >= base_price * Decimal("0.90")
    
    def test_category_specific_rules(self, engine):
        """Test that category-specific rules are applied."""
        base_price = Decimal("100.00")
        expiry_date = date.today() + timedelta(days=1)
        
        # Dairy category should have higher discount for critical expiry
        computed_dairy, discount_dairy, _ = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50,
            category="Dairy"
        )
        
        # General category
        computed_general, discount_general, _ = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50,
            category=None
        )
        
        # Dairy should have at least as much discount
        assert discount_dairy >= discount_general
    
    def test_preview_discount(self, engine):
        """Test discount preview without actual computation."""
        discount_pct, rule_name = engine.preview_discount(
            days_to_expiry=5,
            quantity=50
        )
        
        assert discount_pct > 0
        assert rule_name is not None
        assert isinstance(rule_name, str)
    
    def test_expired_product_maximum_discount(self, engine):
        """Test that expired products get maximum configured discount."""
        base_price = Decimal("100.00")
        expiry_date = date.today() - timedelta(days=5)  # Expired 5 days ago
        
        computed_price, discount_pct, reason = engine.compute_batch_price(
            base_price=base_price,
            expiry_date=expiry_date,
            quantity=50
        )
        
        assert reason == "expired"
        assert discount_pct == Decimal("0.80")  # Max discount from defaults


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
