from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import prisma
from app.schemas.inventory import (
    InventoryBatchCreate,
    InventoryBatchUpdate,
    InventoryBatchResponse,
    InventoryBatchWithProductResponse,
)


class InventoryService:
    """Service layer for inventory batch operations."""

    @staticmethod
    async def create_batch(batch_data: InventoryBatchCreate) -> InventoryBatchResponse:
        """Create a new inventory batch."""
        # Convert date to datetime for Prisma if needed
        expiry_date = batch_data.expiry_date
        if isinstance(expiry_date, date) and not isinstance(expiry_date, datetime):
            expiry_datetime = datetime.combine(expiry_date, datetime.min.time())
        else:
            expiry_datetime = expiry_date
            
        batch = await prisma.inventorybatch.create(
            data={
                "productId": batch_data.product_id,
                "batchCode": batch_data.batch_code,
                "quantity": batch_data.quantity,
                "expiryDate": expiry_datetime,
            }
        )
        return InventoryBatchResponse.model_validate(batch)

    @staticmethod
    async def get_batch_by_id(batch_id: int) -> Optional[InventoryBatchResponse]:
        """Get an inventory batch by ID."""
        batch = await prisma.inventorybatch.find_unique(where={"id": batch_id})
        if not batch:
            return None
        return InventoryBatchResponse.model_validate(batch)

    @staticmethod
    async def get_batches_by_product(
        product_id: int, skip: int = 0, limit: int = 100
    ) -> List[InventoryBatchResponse]:
        """Get all batches for a specific product."""
        batches = await prisma.inventorybatch.find_many(
            where={"productId": product_id},
            skip=skip,
            take=limit,
            order={"expiryDate": "asc"},
        )
        return [InventoryBatchResponse.model_validate(b) for b in batches]

    @staticmethod
    async def get_all_batches(
        skip: int = 0, limit: int = 100, expiring_soon: bool = False
    ) -> List[InventoryBatchWithProductResponse]:
        """Get all inventory batches with product details."""
        where_clause = {}
        
        if expiring_soon:
            # Get batches expiring within 30 days
            from datetime import timedelta
            threshold_date = date.today() + timedelta(days=30)
            where_clause["expiryDate"] = {"lte": threshold_date}

        batches = await prisma.inventorybatch.find_many(
            where=where_clause,
            skip=skip,
            take=limit,
            include={"product": True, "batchDiscounts": True},
            order={"expiryDate": "asc"},
        )

        result = []
        for batch in batches:
            batch_dict = batch.model_dump()
            
            # Calculate days to expiry
            expiry_date = batch.expiryDate
            if isinstance(expiry_date, datetime):
                expiry_date = expiry_date.date()
            days_to_expiry = (expiry_date - date.today()).days
            
            # Get current discount if available
            current_discount_pct = None
            if batch.batchDiscounts:
                active_discount = None
                for discount in batch.batchDiscounts:
                    if discount.validTo is None or discount.validTo > datetime.now():
                        active_discount = discount
                        break
                if active_discount:
                    current_discount_pct = active_discount.discountPct

            batch_response = InventoryBatchWithProductResponse(
                **batch_dict,
                product_name=batch.product.name if batch.product else None,
                product_sku=batch.product.sku if batch.product else None,
                days_to_expiry=days_to_expiry,
                current_discount_pct=current_discount_pct,
            )
            result.append(batch_response)

        return result

    @staticmethod
    async def get_expiring_batches(days_threshold: int = 30) -> List[InventoryBatchResponse]:
        """Get batches expiring within specified days."""
        from datetime import timedelta
        threshold_date = date.today() + timedelta(days=days_threshold)
        
        batches = await prisma.inventorybatch.find_many(
            where={
                "expiryDate": {"lte": threshold_date},
                "quantity": {"gt": 0},
            },
            order={"expiryDate": "asc"},
        )
        return [InventoryBatchResponse.model_validate(b) for b in batches]

    @staticmethod
    async def update_batch(
        batch_id: int, batch_data: InventoryBatchUpdate
    ) -> Optional[InventoryBatchResponse]:
        """Update an inventory batch."""
        # Build update data dict with only provided fields
        update_data = {}
        if batch_data.batch_code is not None:
            update_data["batchCode"] = batch_data.batch_code
        if batch_data.quantity is not None:
            update_data["quantity"] = batch_data.quantity
        if batch_data.expiry_date is not None:
            update_data["expiryDate"] = batch_data.expiry_date

        if not update_data:
            return await InventoryService.get_batch_by_id(batch_id)

        batch = await prisma.inventorybatch.update(
            where={"id": batch_id}, data=update_data
        )
        return InventoryBatchResponse.model_validate(batch)

    @staticmethod
    async def delete_batch(batch_id: int) -> bool:
        """Delete an inventory batch."""
        try:
            await prisma.inventorybatch.delete(where={"id": batch_id})
            return True
        except Exception:
            return False

    @staticmethod
    async def update_batch_quantity(batch_id: int, quantity_delta: int) -> Optional[InventoryBatchResponse]:
        """Update batch quantity by delta (can be positive or negative)."""
        batch = await prisma.inventorybatch.find_unique(where={"id": batch_id})
        if not batch:
            return None

        new_quantity = batch.quantity + quantity_delta
        if new_quantity < 0:
            raise ValueError("Insufficient quantity in batch")

        updated_batch = await prisma.inventorybatch.update(
            where={"id": batch_id}, data={"quantity": new_quantity}
        )
        return InventoryBatchResponse.model_validate(updated_batch)
