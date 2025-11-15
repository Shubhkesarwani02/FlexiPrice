from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from decimal import Decimal

from app.schemas.product import ProductWithDiscountResponse
from app.services.product_service import ProductService
from app.services.discount_service import DiscountService

router = APIRouter()


@router.get(
    "/products",
    response_model=List[ProductWithDiscountResponse],
    summary="Get products with current prices (storefront)",
)
async def get_storefront_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Public endpoint for storefront to get products with their current discounted prices.
    
    Returns products with:
    - Current discount percentage (if any)
    - Discounted price
    - Nearest expiry date
    
    This is the primary endpoint for frontend/storefront integration.
    """
    try:
        # Use the existing service method that includes discount info
        return await ProductService.get_products_with_discounts(
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}",
        )


@router.get(
    "/products/{product_id}/best-price",
    response_model=dict,
    summary="Get best available price for a product",
)
async def get_product_best_price(product_id: int):
    """
    Get the best (lowest) available price for a product.
    
    Searches across all batches and returns the lowest discounted price.
    Useful for:
    - Price comparison
    - Showing "starting at" prices
    - Finding best deals
    """
    try:
        best_price = await DiscountService.get_product_best_price(product_id)
        
        if best_price is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found or has no inventory",
            )
        
        # Also get product details for context
        product = await ProductService.get_product_by_id(product_id)
        
        return {
            "product_id": product_id,
            "product_name": product.name if product else None,
            "base_price": product.base_price if product else None,
            "best_price": best_price,
            "savings": (product.base_price - best_price) if product else Decimal("0.0"),
            "discount_pct": (
                ((product.base_price - best_price) / product.base_price * Decimal("100.0"))
                if product and product.base_price > 0
                else Decimal("0.0")
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get best price: {str(e)}",
        )
