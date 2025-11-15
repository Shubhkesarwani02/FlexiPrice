"""
Batch Discount Service

Service for managing batch-level discount writes and retrievals.
Optimized for bulk operations and performance.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.core.database import prisma

logger = logging.getLogger(__name__)


class BatchDiscountService:
    """Service for batch discount operations."""

    @staticmethod
    async def write_batch_discounts(
        discount_data: List[Dict],
        batch_size: int = 100
    ) -> Dict[str, int]:
        """
        Write multiple batch discounts efficiently.
        
        Args:
            discount_data: List of dicts with keys: batch_id, computed_price, 
                          discount_pct, expires_at
            batch_size: Number of records to insert at once
            
        Returns:
            Dict with statistics
        """
        stats = {
            "created": 0,
            "updated": 0,
            "errors": 0
        }
        
        # Process in chunks for better performance
        for i in range(0, len(discount_data), batch_size):
            chunk = discount_data[i:i + batch_size]
            
            for data in chunk:
                try:
                    batch_id = data["batch_id"]
                    
                    # Check if active discount exists
                    existing = await prisma.batchdiscount.find_first(
                        where={
                            "batchId": batch_id,
                            "OR": [
                                {"validTo": None},
                                {"validTo": {"gt": datetime.now()}}
                            ]
                        }
                    )
                    
                    if existing:
                        # Update if price changed significantly
                        price_diff = abs(
                            float(existing.computedPrice) - 
                            float(data["computed_price"])
                        )
                        
                        if price_diff > 0.01:  # More than 1 cent
                            await prisma.batchdiscount.update(
                                where={"id": existing.id},
                                data={
                                    "computedPrice": data["computed_price"],
                                    "discountPct": data["discount_pct"],
                                    "expiresAt": data.get("expires_at"),
                                }
                            )
                            stats["updated"] += 1
                    else:
                        # Create new discount
                        await prisma.batchdiscount.create(
                            data={
                                "batchId": batch_id,
                                "computedPrice": data["computed_price"],
                                "discountPct": data["discount_pct"],
                                "validFrom": datetime.now(),
                                "expiresAt": data.get("expires_at"),
                                "mlRecommended": data.get("ml_recommended", False),
                            }
                        )
                        stats["created"] += 1
                        
                except Exception as e:
                    logger.error(f"Error writing discount for batch {data.get('batch_id')}: {e}")
                    stats["errors"] += 1
        
        return stats

    @staticmethod
    async def get_active_batch_discounts(
        product_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Get all active batch discounts, optionally filtered by products.
        
        Args:
            product_ids: Optional list of product IDs to filter
            
        Returns:
            List of active discounts with batch and product info
        """
        where_clause = {
            "OR": [
                {"validTo": None},
                {"validTo": {"gt": datetime.now()}}
            ]
        }
        
        # Add product filter if provided
        if product_ids:
            where_clause["batch"] = {
                "productId": {"in": product_ids}
            }
        
        discounts = await prisma.batchdiscount.find_many(
            where=where_clause,
            include={
                "batch": {
                    "include": {
                        "product": True
                    }
                }
            }
        )
        
        return [d.model_dump() for d in discounts]

    @staticmethod
    async def get_storefront_prices(
        product_ids: List[int]
    ) -> Dict[int, Tuple[Decimal, Optional[Decimal]]]:
        """
        Calculate storefront prices for products.
        
        Returns the minimum computed_price from active batches,
        or base price if no active discounts.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            Dict mapping product_id to (storefront_price, discount_pct)
        """
        # Get products with their batches and discounts
        products = await prisma.product.find_many(
            where={"id": {"in": product_ids}},
            include={
                "inventoryBatches": {
                    "include": {
                        "batchDiscounts": {
                            "where": {
                                "OR": [
                                    {"validTo": None},
                                    {"validTo": {"gt": datetime.now()}}
                                ]
                            },
                            "order_by": {"computedPrice": "asc"},
                            "take": 1
                        }
                    },
                    "where": {"quantity": {"gt": 0}}
                }
            }
        )
        
        result = {}
        
        for product in products:
            min_price = product.basePrice
            best_discount = None
            
            # Find minimum price across all active batch discounts
            for batch in product.inventoryBatches:
                if batch.batchDiscounts:
                    discount = batch.batchDiscounts[0]
                    if discount.computedPrice < min_price:
                        min_price = discount.computedPrice
                        best_discount = discount.discountPct
            
            result[product.id] = (min_price, best_discount)
        
        return result

    @staticmethod
    async def expire_old_discounts(days: int = 0) -> int:
        """
        Mark discounts as expired based on expiresAt field.
        
        Args:
            days: Expire discounts older than this many days (0 = today)
            
        Returns:
            Number of discounts expired
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        result = await prisma.batchdiscount.update_many(
            where={
                "expiresAt": {"lt": cutoff},
                "validTo": None
            },
            data={"validTo": datetime.now()}
        )
        
        return result

    @staticmethod
    async def cleanup_expired_batch_discounts() -> int:
        """
        Clean up discounts for expired inventory batches.
        
        Returns:
            Number of discounts cleaned up
        """
        # Get expired batches
        expired_batches = await prisma.inventorybatch.find_many(
            where={"expiryDate": {"lt": datetime.now()}},
            select={"id": True}
        )
        
        batch_ids = [b.id for b in expired_batches]
        
        if not batch_ids:
            return 0
        
        # Mark their discounts as expired
        result = await prisma.batchdiscount.update_many(
            where={
                "batchId": {"in": batch_ids},
                "validTo": None
            },
            data={"validTo": datetime.now()}
        )
        
        return result
