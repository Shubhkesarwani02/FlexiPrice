from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from prisma.errors import UniqueViolationError

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithDiscountResponse,
    ProductWithStorefrontPriceResponse,
)
from app.services.product_service import ProductService

router = APIRouter()


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product: ProductCreate):
    """
    Create a new product with the following information:
    
    - **sku**: Unique product SKU (required)
    - **name**: Product name (required)
    - **description**: Product description (optional)
    - **category**: Product category (optional)
    - **base_price**: Base price of the product (required)
    """
    try:
        return await ProductService.create_product(product)
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku}' already exists",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}",
        )


@router.get(
    "",
    response_model=List[ProductWithStorefrontPriceResponse],
    summary="List all products with storefront prices",
)
async def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Retrieve a list of all products with computed storefront prices.
    
    Storefront price is the minimum computed_price from active batches,
    or base price if no active discounts exist.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **category**: Filter products by category (optional)
    """
    try:
        return await ProductService.get_all_products_with_storefront_price(
            skip=skip, limit=limit, category=category
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}",
        )


@router.get(
    "/with-discounts",
    response_model=List[ProductWithDiscountResponse],
    summary="List products with current discount information",
)
async def list_products_with_discounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    Retrieve products with their current discount information based on expiry dates.
    
    Includes:
    - Current discount percentage (if any)
    - Discounted price
    - Nearest expiry date from inventory batches
    """
    try:
        return await ProductService.get_products_with_discounts(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products with discounts: {str(e)}",
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
)
async def get_product(product_id: int):
    """
    Get a specific product by its ID.
    """
    product = await ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    return product


@router.get(
    "/sku/{sku}",
    response_model=ProductResponse,
    summary="Get product by SKU",
)
async def get_product_by_sku(sku: str):
    """
    Get a specific product by its SKU.
    """
    product = await ProductService.get_product_by_sku(sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
)
async def update_product(product_id: int, product: ProductUpdate):
    """
    Update an existing product. Only provided fields will be updated.
    """
    try:
        updated_product = await ProductService.update_product(product_id, product)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found",
            )
        return updated_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}",
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
async def delete_product(product_id: int):
    """
    Delete a product by ID. This will also delete all associated inventory batches and discounts.
    """
    success = await ProductService.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
