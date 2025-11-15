"""
Discount Engine Module

Rule-based discount calculation engine for expiry-based dynamic pricing.
Supports configurable rules with conditions on days_to_expiry, quantity, and category.
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path
import yaml

from app.core.config import get_settings

settings = get_settings()


class DiscountRule:
    """Represents a single discount rule."""
    
    def __init__(
        self,
        name: str,
        conditions: Dict,
        discount_pct: float,
        price_floor: float,
        description: Optional[str] = None,
    ):
        self.name = name
        self.conditions = conditions
        self.discount_pct = discount_pct
        self.price_floor = price_floor
        self.description = description

    def evaluate(self, days_to_expiry: int, quantity: int, category: Optional[str] = None) -> bool:
        """Evaluate if this rule matches the given conditions."""
        for key, condition in self.conditions.items():
            if key == "days_to_expiry":
                if not self._evaluate_numeric(days_to_expiry, condition):
                    return False
            elif key == "quantity":
                if not self._evaluate_numeric(quantity, condition):
                    return False
            elif key == "category":
                if category and category.lower() != condition.lower():
                    return False
        return True

    def _evaluate_numeric(self, value: int, condition: str) -> bool:
        """Evaluate numeric conditions like '<=7', '>100', etc."""
        condition = condition.strip()
        
        if condition.startswith("<="):
            return value <= int(condition[2:])
        elif condition.startswith(">="):
            return value >= int(condition[2:])
        elif condition.startswith("<"):
            return value < int(condition[1:])
        elif condition.startswith(">"):
            return value > int(condition[1:])
        elif condition.startswith("=="):
            return value == int(condition[2:])
        else:
            # Default to equality
            return value == int(condition)

    def __repr__(self):
        return f"<DiscountRule(name='{self.name}', discount={self.discount_pct}%)>"


class DiscountEngine:
    """
    Core discount calculation engine.
    
    Loads rules from configuration and computes optimal pricing
    based on expiry dates, inventory levels, and other factors.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the discount engine with rules configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "discount_rules.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.global_settings = self.config.get("global", {})
        self.rules = self._parse_rules(self.config.get("rules", []))
        self.category_rules = self._parse_category_rules(self.config.get("category_rules", {}))

    def _load_config(self) -> Dict:
        """Load discount rules from YAML configuration file."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: Config file not found at {self.config_path}")
            return {"global": {}, "rules": []}
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {"global": {}, "rules": []}

    def _parse_rules(self, rules_config: List[Dict]) -> List[DiscountRule]:
        """Parse rules configuration into DiscountRule objects."""
        rules = []
        for rule_data in rules_config:
            rule = DiscountRule(
                name=rule_data.get("name", "Unnamed Rule"),
                conditions=rule_data.get("conditions", {}),
                discount_pct=rule_data.get("discount_pct", 0.0),
                price_floor=rule_data.get("price_floor", self.global_settings.get("default_price_floor", 0.3)),
                description=rule_data.get("description"),
            )
            rules.append(rule)
        return rules

    def _parse_category_rules(self, category_config: Dict) -> Dict[str, List[DiscountRule]]:
        """Parse category-specific rules."""
        category_rules = {}
        for category, data in category_config.items():
            category_rules[category.lower()] = self._parse_rules(data.get("rules", []))
        return category_rules

    def compute_batch_price(
        self,
        base_price: Decimal,
        days_to_expiry: int,
        quantity: int,
        category: Optional[str] = None,
        min_price_floor: Optional[float] = None,
    ) -> Tuple[Decimal, Decimal, str]:
        """
        Compute the optimal price for a batch based on rules.
        
        Args:
            base_price: Original price of the product
            days_to_expiry: Number of days until expiry
            quantity: Current inventory quantity
            category: Product category (optional)
            min_price_floor: Minimum price as fraction of base_price (optional override)
        
        Returns:
            Tuple of (computed_price, discount_percentage, rule_name)
        """
        # Determine which rules to use
        applicable_rules = self.rules
        if category and category.lower() in self.category_rules:
            # Category-specific rules take precedence
            applicable_rules = self.category_rules[category.lower()] + self.rules

        # Find first matching rule
        matched_rule = None
        for rule in applicable_rules:
            if rule.evaluate(days_to_expiry, quantity, category):
                matched_rule = rule
                break

        # No matching rule - return base price
        if not matched_rule:
            return base_price, Decimal("0.0"), "No Discount"

        # Calculate discounted price
        discount_pct = Decimal(str(matched_rule.discount_pct))
        discount_multiplier = Decimal("1.0") - (discount_pct / Decimal("100.0"))
        computed_price = base_price * discount_multiplier

        # Apply price floor
        price_floor = min_price_floor if min_price_floor is not None else matched_rule.price_floor
        min_price = base_price * Decimal(str(price_floor))
        
        if computed_price < min_price:
            computed_price = min_price
            # Recalculate actual discount percentage
            discount_pct = ((base_price - computed_price) / base_price * Decimal("100.0"))

        # Ensure discount is within global bounds
        min_discount = Decimal(str(self.global_settings.get("min_discount_pct", 0.0)))
        max_discount = Decimal(str(self.global_settings.get("max_discount_pct", 80.0)))
        discount_pct = max(min_discount, min(discount_pct, max_discount))

        # Round to 2 decimal places
        computed_price = computed_price.quantize(Decimal("0.01"))
        discount_pct = discount_pct.quantize(Decimal("0.01"))

        return computed_price, discount_pct, matched_rule.name

    def calculate_days_to_expiry(self, expiry_date: date) -> int:
        """Calculate days remaining until expiry."""
        today = date.today()
        delta = expiry_date - today
        return delta.days

    def get_applicable_rules(
        self,
        days_to_expiry: int,
        quantity: int,
        category: Optional[str] = None,
    ) -> List[DiscountRule]:
        """Get all rules that would apply to given conditions."""
        applicable_rules = []
        
        # Check general rules
        for rule in self.rules:
            if rule.evaluate(days_to_expiry, quantity, category):
                applicable_rules.append(rule)
        
        # Check category-specific rules
        if category and category.lower() in self.category_rules:
            for rule in self.category_rules[category.lower()]:
                if rule.evaluate(days_to_expiry, quantity, category):
                    applicable_rules.append(rule)
        
        return applicable_rules

    def reload_config(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        self.global_settings = self.config.get("global", {})
        self.rules = self._parse_rules(self.config.get("rules", []))
        self.category_rules = self._parse_category_rules(self.config.get("category_rules", {}))
        print("✅ Discount rules reloaded")


# Global discount engine instance
_discount_engine: Optional[DiscountEngine] = None


def get_discount_engine() -> DiscountEngine:
    """Get or create the global discount engine instance."""
    global _discount_engine
    if _discount_engine is None:
        _discount_engine = DiscountEngine()
    return _discount_engine


# Convenience function for direct use
def compute_batch_price(
    base_price: Decimal,
    days_to_expiry: int,
    quantity: int,
    category: Optional[str] = None,
    min_price_floor: Optional[float] = None,
) -> Tuple[Decimal, Decimal, str]:
    """
    Compute batch price using the global discount engine.
    
    This is a convenience wrapper around DiscountEngine.compute_batch_price().
    """
    engine = get_discount_engine()
    return engine.compute_batch_price(
        base_price=base_price,
        days_to_expiry=days_to_expiry,
        quantity=quantity,
        category=category,
        min_price_floor=min_price_floor,
    )
