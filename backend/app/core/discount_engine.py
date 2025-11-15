"""
Discount Engine Module for FlexiPrice

This module implements the core discount calculation logic based on configurable rules.
Rules are evaluated against inventory batches to compute optimal discounts.
"""

import yaml
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from pathlib import Path
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)


class DiscountRule:
    """Represents a single discount rule with conditions and discount percentage."""
    
    def __init__(self, name: str, condition: Dict, discount: float, priority: int):
        self.name = name
        self.condition = condition
        self.discount = discount
        self.priority = priority
    
    def evaluate(self, days_to_expiry: int, quantity: int) -> bool:
        """
        Evaluate if this rule matches the given conditions.
        
        Args:
            days_to_expiry: Number of days until the batch expires
            quantity: Current quantity in the batch
            
        Returns:
            True if rule conditions are met, False otherwise
        """
        # Evaluate days_to_expiry conditions
        if "days_to_expiry" in self.condition:
            dte_cond = self.condition["days_to_expiry"]
            
            if isinstance(dte_cond, dict):
                # Handle range conditions (lte, gte, gt, lt)
                if "lte" in dte_cond and days_to_expiry > dte_cond["lte"]:
                    return False
                if "gte" in dte_cond and days_to_expiry < dte_cond["gte"]:
                    return False
                if "gt" in dte_cond and days_to_expiry <= dte_cond["gt"]:
                    return False
                if "lt" in dte_cond and days_to_expiry >= dte_cond["lt"]:
                    return False
            else:
                # Exact match
                if days_to_expiry != dte_cond:
                    return False
        
        # Evaluate quantity conditions
        if "quantity" in self.condition:
            qty_cond = self.condition["quantity"]
            
            if isinstance(qty_cond, dict):
                if "lte" in qty_cond and quantity > qty_cond["lte"]:
                    return False
                if "gte" in qty_cond and quantity < qty_cond["gte"]:
                    return False
                if "gt" in qty_cond and quantity <= qty_cond["gt"]:
                    return False
                if "lt" in qty_cond and quantity >= qty_cond["lt"]:
                    return False
            else:
                if quantity != qty_cond:
                    return False
        
        return True


class DiscountEngine:
    """
    Core discount computation engine.
    
    Loads rules from YAML configuration and applies them to inventory batches
    to compute optimal discount percentages and prices.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the discount engine.
        
        Args:
            config_path: Path to discount rules YAML file. If None, uses default.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "discount_rules.yaml"
        
        self.config_path = Path(config_path)
        self.rules: List[DiscountRule] = []
        self.defaults: Dict = {}
        self.category_overrides: Dict = {}
        
        self._load_rules()
    
    def _load_rules(self):
        """Load discount rules from YAML configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load default settings
            self.defaults = config.get('defaults', {})
            
            # Load general rules
            for rule_data in config.get('rules', []):
                rule = DiscountRule(
                    name=rule_data['name'],
                    condition=rule_data['condition'],
                    discount=rule_data['discount'],
                    priority=rule_data.get('priority', 999)
                )
                self.rules.append(rule)
            
            # Sort rules by priority (lower number = higher priority)
            self.rules.sort(key=lambda r: r.priority)
            
            # Load category-specific overrides
            self.category_overrides = config.get('category_overrides', {})
            
            logger.info(f"Loaded {len(self.rules)} discount rules from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load discount rules: {e}")
            raise
    
    def _get_rules_for_category(self, category: Optional[str]) -> List[DiscountRule]:
        """Get rules applicable for a specific category."""
        if category and category in self.category_overrides:
            override = self.category_overrides[category]
            if 'rules' in override:
                # Use category-specific rules
                category_rules = []
                for rule_data in override['rules']:
                    rule = DiscountRule(
                        name=rule_data['name'],
                        condition=rule_data['condition'],
                        discount=rule_data['discount'],
                        priority=rule_data.get('priority', 999)
                    )
                    category_rules.append(rule)
                category_rules.sort(key=lambda r: r.priority)
                return category_rules
        
        # Return general rules
        return self.rules
    
    def _get_price_floor_multiplier(self, category: Optional[str]) -> float:
        """Get price floor multiplier for a category."""
        if category and category in self.category_overrides:
            override = self.category_overrides[category]
            if 'price_floor_multiplier' in override:
                return override['price_floor_multiplier']
        
        return self.defaults.get('price_floor_multiplier', 0.20)
    
    def compute_batch_price(
        self,
        base_price: Decimal,
        expiry_date: date,
        quantity: int,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None
    ) -> Tuple[Decimal, Decimal, str]:
        """
        Compute discounted price for an inventory batch based on rules.
        
        Args:
            base_price: Original/base price of the product
            expiry_date: Expiry date of the batch
            quantity: Current quantity in the batch
            category: Product category (for category-specific rules)
            min_price: Optional minimum price override
            
        Returns:
            Tuple of (computed_price, discount_percentage, reason)
            - computed_price: Final price after discount
            - discount_percentage: Discount as decimal (0.30 = 30%)
            - reason: Explanation of which rule was applied
        """
        # Calculate days to expiry
        days_to_expiry = (expiry_date - date.today()).days
        
        # If already expired, apply maximum discount
        if days_to_expiry < 0:
            max_discount = self.defaults.get('max_discount', 0.80)
            computed_price = base_price * Decimal(1 - max_discount)
            return computed_price, Decimal(max_discount), "expired"
        
        # Get applicable rules for this category
        rules = self._get_rules_for_category(category)
        
        # Find first matching rule
        matched_rule = None
        for rule in rules:
            if rule.evaluate(days_to_expiry, quantity):
                matched_rule = rule
                break
        
        # Apply discount
        if matched_rule:
            discount_pct = Decimal(str(matched_rule.discount))
            discount_pct = self._clamp_discount(discount_pct)
            computed_price = base_price * (Decimal('1.0') - discount_pct)
            reason = matched_rule.name
        else:
            # No rule matched - use minimum discount
            discount_pct = Decimal(str(self.defaults.get('min_discount', 0.0)))
            computed_price = base_price
            reason = "no_rule_matched"
        
        # Apply price floor
        if min_price is None:
            floor_multiplier = Decimal(str(self._get_price_floor_multiplier(category)))
            min_price = base_price * floor_multiplier
        
        computed_price = max(computed_price, min_price)
        
        # Recalculate actual discount based on final price
        actual_discount = (base_price - computed_price) / base_price
        
        logger.debug(
            f"Computed price for batch: base={base_price}, days={days_to_expiry}, "
            f"qty={quantity}, discount={actual_discount:.2%}, price={computed_price}, "
            f"reason={reason}"
        )
        
        return computed_price, actual_discount, reason
    
    def _clamp_discount(self, discount: Decimal) -> Decimal:
        """Clamp discount percentage to configured min/max bounds."""
        min_discount = Decimal(str(self.defaults.get('min_discount', 0.0)))
        max_discount = Decimal(str(self.defaults.get('max_discount', 0.80)))
        
        return max(min_discount, min(discount, max_discount))
    
    def preview_discount(
        self,
        days_to_expiry: int,
        quantity: int,
        category: Optional[str] = None
    ) -> Tuple[float, str]:
        """
        Preview what discount would be applied for given conditions.
        
        Useful for testing and UI previews without actual price calculation.
        
        Args:
            days_to_expiry: Days until expiry
            quantity: Batch quantity
            category: Product category
            
        Returns:
            Tuple of (discount_percentage, rule_name)
        """
        rules = self._get_rules_for_category(category)
        
        for rule in rules:
            if rule.evaluate(days_to_expiry, quantity):
                return rule.discount, rule.name
        
        return self.defaults.get('min_discount', 0.0), "no_rule_matched"
    
    def reload_rules(self):
        """Reload rules from configuration file."""
        self.rules.clear()
        self.defaults.clear()
        self.category_overrides.clear()
        self._load_rules()
        logger.info("Discount rules reloaded")


# Global discount engine instance
_engine_instance: Optional[DiscountEngine] = None


def get_discount_engine() -> DiscountEngine:
    """Get or create the global discount engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = DiscountEngine()
    return _engine_instance
