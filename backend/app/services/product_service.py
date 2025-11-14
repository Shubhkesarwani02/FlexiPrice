from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.core.database import prisma
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithDiscountResponse,
)


class ProductService:
    """Service layer for product operations."""

    @staticmethod
    async def create_product(product_data: ProductCreate) -> ProductResponse:
        """Create a new product."""
        product = await prisma.product.create(
            data={
                "sku": product_data.sku,
                "name": product_data.name,
                "description": product_data.description,
                "category": product_data.category,
                "basePrice": product_data.base_price,
            }
        )
        return ProductResponse.model_validate(product)

    @staticmethod
    async def get_product_by_id(product_id: int) -> Optional[ProductResponse]:
        """Get a product by ID."""
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            return None
        return ProductResponse.model_validate(product)

    @staticmethod
    async def get_product_by_sku(sku: str) -> Optional[ProductResponse]:
        """Get a product by SKU."""
        product = await prisma.product.find_unique(where={"sku": sku})
        if not product:
            return None
        return ProductResponse.model_validate(product)

    @staticmethod
    async def get_all_products(
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
    ) -> List[ProductResponse]:
        """Get all products with optional filtering."""
        where_clause = {}
        if category:
            where_clause["category"] = category

        products = await prisma.product.find_many(
            where=where_clause,
            skip=skip,
            take=limit,
            order={"createdAt": "desc"},
        )
        return [ProductResponse.model_validate(p) for p in products]

    @staticmethod
    async def get_products_with_discounts(
        skip: int = 0, limit: int = 100
    ) -> List[ProductWithDiscountResponse]:
        """Get products with their current discount information."""
        products = await prisma.product.find_many(
            skip=skip,
            take=limit,
            include={
                "inventoryBatches": {
                    "include": {"batchDiscounts": True},
                    "order_by": {"expiryDate": "asc"},
                    "take": 1,
                }
            },
            order={"createdAt": "desc"},
        )

        result = []
        for product in products:
            product_dict = product.model_dump()
            
            # Calculate discount info from nearest expiry batch
            current_discount_pct = None
            discounted_price = None
            nearest_expiry = None

            if product.inventoryBatches:
                batch = product.inventoryBatches[0]
                nearest_expiry = batch.expiryDate
                
                if batch.batchDiscounts:
                    # Get the most recent active discount
                    active_discount = None
                    for discount in batch.batchDiscounts:
                        if discount.validTo is None or discount.validTo > datetime.now():
                            active_discount = discount
                            break
                    
                    if active_discount:
                        current_discount_pct = active_discount.discountPct
                        discounted_price = active_discount.computedPrice

            product_response = ProductWithDiscountResponse(
                **product_dict,
                current_discount_pct=current_discount_pct,
                discounted_price=discounted_price,
                nearest_expiry=nearest_expiry,
            )
            result.append(product_response)

        return result

    @staticmethod
    async def update_product(
        product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        """Update a product."""
        # Build update data dict with only provided fields
        update_data = {}
        if product_data.name is not None:
            update_data["name"] = product_data.name
        if product_data.description is not None:
            update_data["description"] = product_data.description
        if product_data.category is not None:
            update_data["category"] = product_data.category
        if product_data.base_price is not None:
            update_data["basePrice"] = product_data.base_price

        if not update_data:
            return await ProductService.get_product_by_id(product_id)

        product = await prisma.product.update(
            where={"id": product_id}, data=update_data
        )
        return ProductResponse.model_validate(product)

    @staticmethod
    async def delete_product(product_id: int) -> bool:
        """Delete a product."""
        try:
            await prisma.product.delete(where={"id": product_id})
            return True
        except Exception:
            return False

    @staticmethod
    async def count_products(category: Optional[str] = None) -> int:
        """Count total products."""
        where_clause = {}
        if category:
            where_clause["category"] = category
        return await prisma.product.count(where=where_clause)
