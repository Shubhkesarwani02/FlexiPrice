"""
A/B Testing Service
Manages experiment assignments and recommendations based on experiment groups.
"""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from app.schemas.experiment import (
    ExperimentGroup,
    ExperimentAssignment,
    ExperimentMetric,
    ExperimentSummary,
    ExperimentComparison,
    RecommendationResponse,
)


class ABTestService:
    """Service for managing A/B experiments."""
    
    @staticmethod
    def assign_experiments(
        product_ids: List[int],
        experiment_group: ExperimentGroup,
        db_products: List[Any]  # Product models from DB
    ) -> List[ExperimentAssignment]:
        """
        Assign products to experiment group.
        
        Args:
            product_ids: List of product IDs to assign
            experiment_group: Group to assign products to
            db_products: Product database records
            
        Returns:
            List of experiment assignments
        """
        assignments = []
        now = datetime.utcnow()
        
        for product in db_products:
            if product.id in product_ids:
                assignments.append(ExperimentAssignment(
                    product_id=product.id,
                    sku=product.sku,
                    experiment_group=experiment_group,
                    assigned_at=now
                ))
        
        return assignments
    
    @staticmethod
    def random_assignment(product_ids: List[int], split_ratio: float = 0.5) -> Dict[ExperimentGroup, List[int]]:
        """
        Randomly assign products to experiment groups.
        
        Args:
            product_ids: List of product IDs to split
            split_ratio: Fraction to assign to control (default 0.5 = 50/50)
            
        Returns:
            Dictionary mapping experiment group to product IDs
        """
        shuffled = product_ids.copy()
        random.shuffle(shuffled)
        
        split_point = int(len(shuffled) * split_ratio)
        
        return {
            ExperimentGroup.CONTROL: shuffled[:split_point],
            ExperimentGroup.ML_VARIANT: shuffled[split_point:]
        }
    
    @staticmethod
    def get_rule_based_recommendation(
        base_price: float,
        days_to_expiry: int,
        inventory: int,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate rule-based discount recommendation.
        
        Rules:
        - 1-2 days: 40-50% off
        - 3-5 days: 25-35% off
        - 6-7 days: 15-25% off
        - 8-14 days: 10-20% off
        - 15+ days: 5-10% off
        
        Adjustments:
        - High inventory (>20): +5% discount
        - Seafood/Produce: +5% discount (perishable)
        """
        # Base discount by expiry
        if days_to_expiry <= 2:
            base_discount = 45.0
            reason = "Critical expiry (≤2 days)"
        elif days_to_expiry <= 5:
            base_discount = 30.0
            reason = "Urgent expiry (3-5 days)"
        elif days_to_expiry <= 7:
            base_discount = 20.0
            reason = "Week expiry (6-7 days)"
        elif days_to_expiry <= 14:
            base_discount = 15.0
            reason = "Two-week expiry (8-14 days)"
        else:
            base_discount = 7.5
            reason = "Long shelf life (15+ days)"
        
        # Inventory adjustment
        if inventory > 20:
            base_discount += 5.0
            reason += " + high inventory"
        
        # Category adjustment
        perishable_categories = ["Seafood", "Produce", "Dairy", "Meat"]
        if category and category in perishable_categories:
            base_discount += 5.0
            reason += f" + perishable ({category})"
        
        # Cap at 50%
        final_discount = min(base_discount, 50.0)
        
        return {
            "discount_pct": final_discount,
            "reason": reason,
            "method": "rule_based"
        }
    
    @staticmethod
    def get_ml_recommendation(
        ml_predictor,
        product_id: int,
        days_to_expiry: int,
        inventory: int,
        top_k: int = 1
    ) -> Dict[str, Any]:
        """
        Get ML-based discount recommendation.
        
        Args:
            ml_predictor: MLPredictor instance
            product_id: Product ID
            days_to_expiry: Days until expiry
            inventory: Current inventory level
            top_k: Number of recommendations (returns best)
            
        Returns:
            Recommendation dict with discount_pct, probability, reason, method
        """
        try:
            recommendations = ml_predictor.recommend_discounts(
                product_id=product_id,
                days_to_expiry=days_to_expiry,
                inventory=inventory,
                top_k=top_k
            )
            
            if recommendations:
                best = recommendations[0]
                return {
                    "discount_pct": float(best["discount_pct"]),
                    "probability": float(best["purchase_probability"]),
                    "reason": f"ML recommendation (prob: {best['purchase_probability']:.1%}, uplift: +{best['uplift_pct']:.0f}%)",
                    "method": "ml"
                }
            else:
                # Fallback to rule-based if ML fails
                return {
                    "discount_pct": 25.0,
                    "probability": None,
                    "reason": "ML fallback (no recommendations available)",
                    "method": "ml_fallback"
                }
                
        except Exception as e:
            # Fallback to rule-based on error
            return {
                "discount_pct": 25.0,
                "probability": None,
                "reason": f"ML error fallback: {str(e)}",
                "method": "ml_error"
            }
    
    @staticmethod
    def calculate_experiment_summary(metrics: List[ExperimentMetric]) -> ExperimentSummary:
        """
        Calculate summary statistics for an experiment group.
        
        Args:
            metrics: List of experiment metrics for products in the group
            
        Returns:
            Aggregated summary for the group
        """
        if not metrics:
            return ExperimentSummary(
                experiment_group=ExperimentGroup.CONTROL,
                total_products=0,
                total_impressions=0,
                total_conversions=0,
                total_revenue=Decimal("0.00"),
                total_units_sold=0,
                avg_discount_pct=Decimal("0.00"),
                conversion_rate=Decimal("0.00"),
                revenue_per_product=Decimal("0.00")
            )
        
        experiment_group = metrics[0].experiment_group
        total_products = len(metrics)
        total_impressions = sum(m.impressions for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_revenue = sum(m.revenue for m in metrics)
        total_units_sold = sum(m.units_sold for m in metrics)
        
        # Calculate averages
        avg_discount = sum(
            m.avg_discount_pct or Decimal("0.00") for m in metrics
        ) / total_products if total_products > 0 else Decimal("0.00")
        
        conversion_rate = (
            Decimal(str(total_conversions / total_impressions * 100))
            if total_impressions > 0 else Decimal("0.00")
        )
        
        revenue_per_product = (
            total_revenue / total_products if total_products > 0 else Decimal("0.00")
        )
        
        return ExperimentSummary(
            experiment_group=experiment_group,
            total_products=total_products,
            total_impressions=total_impressions,
            total_conversions=total_conversions,
            total_revenue=total_revenue,
            total_units_sold=total_units_sold,
            avg_discount_pct=avg_discount,
            conversion_rate=conversion_rate,
            revenue_per_product=revenue_per_product
        )
    
    @staticmethod
    def compare_experiments(
        control_summary: ExperimentSummary,
        ml_summary: ExperimentSummary,
        period_start: datetime,
        period_end: datetime
    ) -> ExperimentComparison:
        """
        Compare ML variant performance against control.
        
        Args:
            control_summary: Control group summary
            ml_summary: ML variant group summary
            period_start: Start of comparison period
            period_end: End of comparison period
            
        Returns:
            Comparison with lift calculations
        """
        # Calculate lifts (percentage improvement)
        conversion_lift = (
            ((ml_summary.conversion_rate - control_summary.conversion_rate) 
             / control_summary.conversion_rate * 100)
            if control_summary.conversion_rate > 0 else Decimal("0.00")
        )
        
        revenue_lift = (
            ((ml_summary.revenue_per_product - control_summary.revenue_per_product)
             / control_summary.revenue_per_product * 100)
            if control_summary.revenue_per_product > 0 else Decimal("0.00")
        )
        
        units_lift = (
            Decimal(str(
                (ml_summary.total_units_sold / ml_summary.total_products 
                 - control_summary.total_units_sold / control_summary.total_products)
                / (control_summary.total_units_sold / control_summary.total_products) * 100
            ))
            if control_summary.total_products > 0 and ml_summary.total_products > 0
               and control_summary.total_units_sold > 0
            else Decimal("0.00")
        )
        
        return ExperimentComparison(
            control=control_summary,
            ml_variant=ml_summary,
            conversion_lift=conversion_lift,
            revenue_lift=revenue_lift,
            units_lift=units_lift,
            period_start=period_start,
            period_end=period_end
        )


# Singleton instance
ab_test_service = ABTestService()
