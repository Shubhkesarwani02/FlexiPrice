"""
Celery Background Tasks

Periodic and asynchronous tasks for discount computation, cleanup, and analytics.
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict

from prisma import Prisma
from app.celery_app import celery_app
from app.core.database import prisma
from app.core.discount_engine import get_discount_engine
from app.services.discount_service import DiscountService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.recompute_all_discounts")
def recompute_all_discounts(days_threshold: int = 30) -> Dict[str, int]:
    """
    Recompute discounts for all eligible inventory batches.
    
    This task:
    1. Queries all batches expiring within the threshold
    2. Calculates optimal discounts using the discount engine
    3. Updates or creates discount records
    
    Args:
        days_threshold: Only process batches expiring within this many days
        
    Returns:
        Dict with processing statistics
    """
    logger.info(f"Starting discount recomputation for batches expiring within {days_threshold} days")
    
    try:
        # Import here to avoid circular dependencies
        import asyncio
        from prisma import Prisma
        
        # Create event loop and run async task
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_recompute_discounts_async(days_threshold))
        
        logger.info(f"Discount recomputation complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in recompute_all_discounts: {str(e)}", exc_info=True)
        raise


async def _recompute_discounts_async(days_threshold: int) -> Dict[str, int]:
    """Async implementation of discount recomputation."""
    db = Prisma()
    await db.connect()
    
    try:
        # Calculate threshold date
        threshold_date_obj = date.today() + timedelta(days=days_threshold)
        threshold_datetime = datetime.combine(threshold_date_obj, datetime.max.time())
        
        # Query batches expiring soon
        batches = await db.inventorybatch.find_many(
            where={
                "expiryDate": {"lte": threshold_datetime},
                "quantity": {"gt": 0}
            },
            include={"product": True, "batchDiscounts": True},
            order={"expiryDate": "asc"}
        )
        
        logger.info(f"Found {len(batches)} batches to process")
        
        stats = {
            "total_processed": 0,
            "discounts_created": 0,
            "discounts_updated": 0,
            "errors": 0
        }
        
        engine = get_discount_engine()
        
        for batch in batches:
            try:
                if not batch.product:
                    logger.warning(f"Batch {batch.id} has no product, skipping")
                    continue
                
                # Convert datetime to date
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
                
                # Check if active discount exists
                active_discount = None
                if batch.batchDiscounts:
                    for disc in batch.batchDiscounts:
                        if disc.validTo is None or disc.validTo > datetime.now():
                            active_discount = disc
                            break
                
                # Create or update discount
                if active_discount:
                    # Update if price changed significantly
                    price_diff = abs(float(active_discount.computedPrice) - float(computed_price))
                    if price_diff > 0.01:  # More than 1 cent difference
                        await db.batchdiscount.update(
                            where={"id": active_discount.id},
                            data={
                                "computedPrice": computed_price,
                                "discountPct": discount_pct,
                            }
                        )
                        stats["discounts_updated"] += 1
                        logger.debug(f"Updated discount for batch {batch.id}: {discount_pct*100:.1f}%")
                else:
                    # Create new discount
                    await db.batchdiscount.create(
                        data={
                            "batchId": batch.id,
                            "computedPrice": computed_price,
                            "discountPct": discount_pct,
                            "validFrom": datetime.now(),
                            "mlRecommended": False,
                        }
                    )
                    stats["discounts_created"] += 1
                    logger.debug(f"Created discount for batch {batch.id}: {discount_pct*100:.1f}%")
                
                stats["total_processed"] += 1
                
            except Exception as e:
                logger.error(f"Error processing batch {batch.id}: {str(e)}")
                stats["errors"] += 1
        
        return stats
        
    finally:
        await db.disconnect()


@celery_app.task(name="app.tasks.cleanup_expired_discounts")
def cleanup_expired_discounts() -> Dict[str, int]:
    """
    Clean up expired discount records.
    
    Marks old discounts as expired by setting validTo timestamp.
    Keeps records for historical analysis.
    
    Returns:
        Dict with cleanup statistics
    """
    logger.info("Starting expired discounts cleanup")
    
    try:
        import asyncio
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_cleanup_discounts_async())
        
        logger.info(f"Cleanup complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_discounts: {str(e)}", exc_info=True)
        raise


async def _cleanup_discounts_async() -> Dict[str, int]:
    """Async implementation of discount cleanup."""
    db = Prisma()
    await db.connect()
    
    try:
        # Find batches that have expired
        expired_batches = await db.inventorybatch.find_many(
            where={
                "expiryDate": {"lt": datetime.now()}
            },
            include={"batchDiscounts": True}
        )
        
        stats = {
            "batches_checked": len(expired_batches),
            "discounts_expired": 0
        }
        
        for batch in expired_batches:
            for discount in batch.batchDiscounts:
                # Mark discount as expired if not already
                if discount.validTo is None:
                    await db.batchdiscount.update(
                        where={"id": discount.id},
                        data={"validTo": datetime.now()}
                    )
                    stats["discounts_expired"] += 1
        
        logger.info(f"Marked {stats['discounts_expired']} discounts as expired")
        return stats
        
    finally:
        await db.disconnect()


@celery_app.task(name="app.tasks.update_price_history")
def update_price_history() -> Dict[str, int]:
    """
    Update price history for products with active discounts.
    
    Records price snapshots for analytics and trend analysis.
    
    Returns:
        Dict with update statistics
    """
    logger.info("Starting price history update")
    
    try:
        import asyncio
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_update_price_history_async())
        
        logger.info(f"Price history update complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in update_price_history: {str(e)}", exc_info=True)
        raise


async def _update_price_history_async() -> Dict[str, int]:
    """Async implementation of price history update."""
    db = Prisma()
    await db.connect()
    
    try:
        # Get all products with active discounts
        products = await db.product.find_many(
            include={
                "inventoryBatches": {
                    "include": {"batchDiscounts": True},
                    "where": {"quantity": {"gt": 0}}
                }
            }
        )
        
        stats = {
            "products_checked": len(products),
            "history_records_created": 0
        }
        
        for product in products:
            # Find lowest current price across all batches
            lowest_price = product.basePrice
            best_discount_pct = Decimal("0.0")
            
            for batch in product.inventoryBatches:
                for discount in batch.batchDiscounts:
                    if discount.validTo is None or discount.validTo > datetime.now():
                        if discount.computedPrice < lowest_price:
                            lowest_price = discount.computedPrice
                            best_discount_pct = discount.discountPct
            
            # Create price history record if there's a discount
            if best_discount_pct > 0:
                await db.pricehistory.create(
                    data={
                        "productId": product.id,
                        "price": lowest_price,
                        "discountPct": best_discount_pct,
                        "reason": "automated_update"
                    }
                )
                stats["history_records_created"] += 1
        
        logger.info(f"Created {stats['history_records_created']} price history records")
        return stats
        
    finally:
        await db.disconnect()


@celery_app.task(name="app.tasks.compute_single_batch_discount")
def compute_single_batch_discount(batch_id: int) -> Dict[str, any]:
    """
    Compute discount for a single batch (on-demand).
    
    This can be triggered manually or by API endpoints for immediate processing.
    
    Args:
        batch_id: ID of the inventory batch
        
    Returns:
        Dict with computation result
    """
    logger.info(f"Computing discount for batch {batch_id}")
    
    try:
        import asyncio
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_compute_single_batch_async(batch_id))
        
        return result
        
    except Exception as e:
        logger.error(f"Error computing discount for batch {batch_id}: {str(e)}", exc_info=True)
        raise


async def _compute_single_batch_async(batch_id: int) -> Dict[str, any]:
    """Async implementation of single batch discount computation."""
    db = Prisma()
    await db.connect()
    
    try:
        batch = await db.inventorybatch.find_unique(
            where={"id": batch_id},
            include={"product": True}
        )
        
        if not batch or not batch.product:
            raise ValueError(f"Batch {batch_id} not found")
        
        engine = get_discount_engine()
        
        # Convert datetime to date
        expiry_date = batch.expiryDate
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        
        computed_price, discount_pct, reason = engine.compute_batch_price(
            base_price=batch.product.basePrice,
            expiry_date=expiry_date,
            quantity=batch.quantity,
            category=batch.product.category
        )
        
        # Create discount record
        discount = await db.batchdiscount.create(
            data={
                "batchId": batch_id,
                "computedPrice": computed_price,
                "discountPct": discount_pct,
                "validFrom": datetime.now(),
                "mlRecommended": False,
            }
        )
        
        return {
            "batch_id": batch_id,
            "discount_id": discount.id,
            "discount_pct": float(discount_pct),
            "computed_price": float(computed_price),
            "reason": reason
        }
        
    finally:
        await db.disconnect()
