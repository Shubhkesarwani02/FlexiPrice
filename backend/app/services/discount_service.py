"""
Discount Service Layer

Handles batch discount computation, persistence, and retrieval.
Integrates the discount engine with database operations.
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import prisma
from app.core.discount_engine import get_discount_engine
from app.schemas.discount import (
    BatchDiscountCreate,
    BatchDiscountResponse,
    DiscountCalculationResponse,
)
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService
import logging

logger = logging.getLogger(__name__)


class DiscountService:
    """Service layer for discount operations."""

    @staticmethod
    async def compute_and_save_discount(
        batch_id: int,
        use_ml_recommendation: bool = False
    ) -> DiscountCalculationResponse:
        """
        Compute discount for a batch and save it to database.
        
        Args:
            batch_id: Inventory batch ID
            use_ml_recommendation: Whether to use ML model (future enhancement)
            
        Returns:
            DiscountCalculationResponse with computed pricing details
        """
        # Get batch with product info
        batch = await prisma.inventorybatch.find_unique(
            where={"id": batch_id},
            include={"product": True}
        )
        
        if not batch:
            raise ValueError(f"Batch with ID {batch_id} not found")
        
        if not batch.product:
            raise ValueError(f"Product not found for batch {batch_id}")
        
        # Get discount engine
        engine = get_discount_engine()
        
        # Convert datetime to date if needed
        expiry_date = batch.expiryDate
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        
        # Compute discount
        computed_price, discount_pct, reason = engine.compute_batch_price(
            base_price=batch.product.basePrice,
            expiry_date=expiry_date,
            quantity=batch.quantity,
            category=batch.product.category
        )
        
        days_to_expiry = (expiry_date - date.today()).days
        
        # Create discount record
        discount = await prisma.batchdiscount.create(
            data={
                "batchId": batch_id,
                "computedPrice": computed_price,
                "discountPct": discount_pct,
                "validFrom": datetime.now(),
                "mlRecommended": use_ml_recommendation,
            }
        )
        
        logger.info(
            f"Created discount for batch {batch_id}: "
            f"{discount_pct:.2%} off, price={computed_price}, reason={reason}"
        )
        
        return DiscountCalculationResponse(
            batch_id=batch_id,
            original_price=batch.product.basePrice,
            discount_pct=discount_pct,
            discounted_price=computed_price,
            days_to_expiry=days_to_expiry,
            ml_recommended=use_ml_recommendation,
            reason=reason
        )
    
    @staticmethod
    async def compute_all_batch_discounts(
        expiring_only: bool = True,
        days_threshold: int = 30
    ) -> List[DiscountCalculationResponse]:
        """
        Compute discounts for multiple batches.
        
        Args:
            expiring_only: Only process batches expiring within threshold
            days_threshold: Days threshold for expiry filtering
            
        Returns:
            List of discount calculation results
        """
        # Get batches to process
        if expiring_only:
            from datetime import timedelta
            threshold_date = date.today() + timedelta(days=days_threshold)
            batches = await prisma.inventorybatch.find_many(
                where={
                    "expiryDate": {"lte": threshold_date},
                    "quantity": {"gt": 0}
                },
                include={"product": True}
            )
        else:
            batches = await prisma.inventorybatch.find_many(
                where={"quantity": {"gt": 0}},
                include={"product": True}
            )
        
        results = []
        engine = get_discount_engine()
        
        for batch in batches:
            try:
                if not batch.product:
                    logger.warning(f"Skipping batch {batch.id}: no product")
                    continue
                
                # Compute discount
                computed_price, discount_pct, reason = engine.compute_batch_price(
                    base_price=batch.product.basePrice,
                    expiry_date=batch.expiryDate,
                    quantity=batch.quantity,
                    category=batch.product.category
                )
                
                days_to_expiry = (batch.expiryDate - date.today()).days
                
                # Invalidate old discounts (set validTo to now)
                await prisma.batchdiscount.update_many(
                    where={
                        "batchId": batch.id,
                        "validTo": None
                    },
                    data={"validTo": datetime.now()}
                )
                
                # Create new discount
                await prisma.batchdiscount.create(
                    data={
                        "batchId": batch.id,
                        "computedPrice": computed_price,
                        "discountPct": discount_pct,
                        "validFrom": datetime.now(),
                        "mlRecommended": False,
                    }
                )
                
                results.append(DiscountCalculationResponse(
                    batch_id=batch.id,
                    original_price=batch.product.basePrice,
                    discount_pct=discount_pct,
                    discounted_price=computed_price,
                    days_to_expiry=days_to_expiry,
                    ml_recommended=False,
                    reason=reason
                ))
                
            except Exception as e:
                logger.error(f"Error computing discount for batch {batch.id}: {e}")
                continue
        
        logger.info(f"Computed discounts for {len(results)} batches")
        return results
    
    @staticmethod
    async def get_active_discount(batch_id: int) -> Optional[BatchDiscountResponse]:
        """Get the currently active discount for a batch."""
        discount = await prisma.batchdiscount.find_first(
            where={
                "batchId": batch_id,
                "OR": [
                    {"validTo": None},
                    {"validTo": {"gt": datetime.now()}}
                ]
            },
            order={"createdAt": "desc"}
        )
        
        if not discount:
            return None
        
        return BatchDiscountResponse.model_validate(discount)
    
    @staticmethod
    async def get_batch_discount_history(
        batch_id: int,
        limit: int = 10
    ) -> List[BatchDiscountResponse]:
        """Get discount history for a batch."""
        discounts = await prisma.batchdiscount.find_many(
            where={"batchId": batch_id},
            order={"createdAt": "desc"},
            take=limit
        )
        
        return [BatchDiscountResponse.model_validate(d) for d in discounts]
    
    @staticmethod
    async def preview_discount(
        batch_id: int
    ) -> DiscountCalculationResponse:
        """
        Preview what discount would be applied without saving.
        
        Useful for testing and UI previews.
        """
        batch = await prisma.inventorybatch.find_unique(
            where={"id": batch_id},
            include={"product": True}
        )
        
        if not batch or not batch.product:
            raise ValueError(f"Batch {batch_id} not found")
        
        # Convert datetime to date if needed
        expiry_date = batch.expiryDate
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        
        engine = get_discount_engine()
        computed_price, discount_pct, reason = engine.compute_batch_price(
            base_price=batch.product.basePrice,
            expiry_date=expiry_date,
            quantity=batch.quantity,
            category=batch.product.category
        )
        
        days_to_expiry = (expiry_date - date.today()).days
        
        return DiscountCalculationResponse(
            batch_id=batch_id,
            original_price=batch.product.basePrice,
            discount_pct=discount_pct,
            discounted_price=computed_price,
            days_to_expiry=days_to_expiry,
            ml_recommended=False,
            reason=reason
        )
