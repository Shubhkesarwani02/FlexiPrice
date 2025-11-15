"""
Discount Service

Business logic for calculating and applying discounts to inventory batches.
Integrates the discount engine with database operations.
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import prisma
from app.core.discount_engine import get_discount_engine, compute_batch_price
from app.schemas.discount import (
    BatchDiscountCreate,
    BatchDiscountResponse,
    DiscountCalculationResponse,
)


class DiscountService:
    """Service for discount calculation and management."""

    @staticmethod
    async def calculate_batch_discount(
        batch_id: int,
        use_ml_recommendation: bool = False,
    ) -> DiscountCalculationResponse:
        """
        Calculate discount for a specific batch.
        
        Args:
            batch_id: ID of the inventory batch
            use_ml_recommendation: Whether to use ML model (future feature)
        
        Returns:
            DiscountCalculationResponse with pricing details
        """
        # Fetch batch with product details
        batch = await prisma.inventorybatch.find_unique(
            where={"id": batch_id},
            include={"product": True},
        )
        
        if not batch or not batch.product:
            raise ValueError(f"Batch with ID {batch_id} not found")

        # Calculate days to expiry
        days_to_expiry = (batch.expiryDate - date.today()).days
        
        # Get base price from product
        base_price = batch.product.basePrice
        
        # Compute discount using engine
        computed_price, discount_pct, rule_name = compute_batch_price(
            base_price=base_price,
            days_to_expiry=days_to_expiry,
            quantity=batch.quantity,
            category=batch.product.category,
        )
        
        return DiscountCalculationResponse(
            batch_id=batch_id,
            original_price=base_price,
            discount_pct=discount_pct,
            discounted_price=computed_price,
            days_to_expiry=days_to_expiry,
            ml_recommended=use_ml_recommendation,
            reason=rule_name,
        )

    @staticmethod
    async def apply_discount_to_batch(
        batch_id: int,
        use_ml_recommendation: bool = False,
        valid_until: Optional[datetime] = None,
    ) -> BatchDiscountResponse:
        """
        Calculate and persist discount for a batch.
        
        Args:
            batch_id: ID of the inventory batch
            use_ml_recommendation: Whether to use ML model
            valid_until: When this discount expires (optional)
        
        Returns:
            BatchDiscountResponse with saved discount
        """
        # Calculate discount
        calc_result = await DiscountService.calculate_batch_discount(
            batch_id=batch_id,
            use_ml_recommendation=use_ml_recommendation,
        )
        
        # Create discount record
        discount = await prisma.batchdiscount.create(
            data={
                "batchId": batch_id,
                "computedPrice": calc_result.discounted_price,
                "discountPct": calc_result.discount_pct,
                "validTo": valid_until,
                "mlRecommended": use_ml_recommendation,
            }
        )
        
        return BatchDiscountResponse.model_validate(discount)

    @staticmethod
    async def calculate_all_expiring_discounts(
        days_threshold: int = 30,
        auto_apply: bool = False,
    ) -> List[DiscountCalculationResponse]:
        """
        Calculate discounts for all batches expiring within threshold.
        
        Args:
            days_threshold: Number of days to look ahead
            auto_apply: Whether to automatically save discounts to database
        
        Returns:
            List of discount calculations
        """
        from datetime import timedelta
        
        threshold_date = date.today() + timedelta(days=days_threshold)
        
        # Get expiring batches
        batches = await prisma.inventorybatch.find_many(
            where={
                "expiryDate": {"lte": threshold_date},
                "quantity": {"gt": 0},
            },
            include={"product": True},
        )
        
        results = []
        for batch in batches:
            if not batch.product:
                continue
                
            days_to_expiry = (batch.expiryDate - date.today()).days
            base_price = batch.product.basePrice
            
            # Compute discount
            computed_price, discount_pct, rule_name = compute_batch_price(
                base_price=base_price,
                days_to_expiry=days_to_expiry,
                quantity=batch.quantity,
                category=batch.product.category,
            )
            
            result = DiscountCalculationResponse(
                batch_id=batch.id,
                original_price=base_price,
                discount_pct=discount_pct,
                discounted_price=computed_price,
                days_to_expiry=days_to_expiry,
                ml_recommended=False,
                reason=rule_name,
            )
            results.append(result)
            
            # Auto-apply if requested
            if auto_apply and discount_pct > 0:
                await DiscountService.apply_discount_to_batch(
                    batch_id=batch.id,
                    use_ml_recommendation=False,
                )
        
        return results

    @staticmethod
    async def get_active_discount_for_batch(batch_id: int) -> Optional[BatchDiscountResponse]:
        """Get the currently active discount for a batch."""
        discount = await prisma.batchdiscount.find_first(
            where={
                "batchId": batch_id,
                "OR": [
                    {"validTo": None},
                    {"validTo": {"gt": datetime.now()}},
                ],
            },
            order={"createdAt": "desc"},
        )
        
        if not discount:
            return None
        
        return BatchDiscountResponse.model_validate(discount)

    @staticmethod
    async def update_batch_discount(
        discount_id: int,
        new_discount_pct: Optional[Decimal] = None,
        new_valid_until: Optional[datetime] = None,
    ) -> Optional[BatchDiscountResponse]:
        """Update an existing discount."""
        update_data = {}
        
        if new_discount_pct is not None:
            update_data["discountPct"] = new_discount_pct
            
            # Recalculate computed price
            discount = await prisma.batchdiscount.find_unique(
                where={"id": discount_id},
                include={"batch": {"include": {"product": True}}},
            )
            
            if discount and discount.batch and discount.batch.product:
                base_price = discount.batch.product.basePrice
                computed_price = base_price * (Decimal("1.0") - new_discount_pct / Decimal("100.0"))
                update_data["computedPrice"] = computed_price
        
        if new_valid_until is not None:
            update_data["validTo"] = new_valid_until
        
        if not update_data:
            return None
        
        updated = await prisma.batchdiscount.update(
            where={"id": discount_id},
            data=update_data,
        )
        
        return BatchDiscountResponse.model_validate(updated)

    @staticmethod
    async def invalidate_discount(discount_id: int) -> bool:
        """Mark a discount as invalid by setting validTo to now."""
        try:
            await prisma.batchdiscount.update(
                where={"id": discount_id},
                data={"validTo": datetime.now()},
            )
            return True
        except Exception:
            return False

    @staticmethod
    async def get_product_best_price(product_id: int) -> Optional[Decimal]:
        """
        Get the best (lowest) available price for a product across all batches.
        
        Returns the lowest discounted price from batches with active discounts,
        or base price if no discounts are active.
        """
        batches = await prisma.inventorybatch.find_many(
            where={
                "productId": product_id,
                "quantity": {"gt": 0},
            },
            include={
                "product": True,
                "batchDiscounts": {
                    "where": {
                        "OR": [
                            {"validTo": None},
                            {"validTo": {"gt": datetime.now()}},
                        ],
                    },
                    "order_by": {"discountPct": "desc"},
                    "take": 1,
                },
            },
        )
        
        if not batches:
            return None
        
        best_price = None
        for batch in batches:
            if batch.batchDiscounts:
                # Use discounted price
                price = batch.batchDiscounts[0].computedPrice
            elif batch.product:
                # Use base price
                price = batch.product.basePrice
            else:
                continue
            
            if best_price is None or price < best_price:
                best_price = price
        
        return best_price
