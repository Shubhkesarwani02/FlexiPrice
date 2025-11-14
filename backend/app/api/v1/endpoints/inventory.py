from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.inventory import (
    InventoryBatchCreate,
    InventoryBatchUpdate,
    InventoryBatchResponse,
    InventoryBatchWithProductResponse,
)
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService

router = APIRouter()


@router.post(
    "",
    response_model=InventoryBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new inventory batch",
)
async def create_inventory_batch(batch: InventoryBatchCreate):
    """
    Add a new inventory batch for a product with expiry date.
    
    - **product_id**: ID of the product (required)
    - **batch_code**: Batch identification code (optional)
    - **quantity**: Quantity in this batch (required)
    - **expiry_date**: Expiry date of this batch (required)
    """
    # Verify product exists
    product = await ProductService.get_product_by_id(batch.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {batch.product_id} not found",
        )
    
    try:
        return await InventoryService.create_batch(batch)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create inventory batch: {str(e)}",
        )


@router.get(
    "",
    response_model=List[InventoryBatchWithProductResponse],
    summary="List all inventory batches",
)
async def list_inventory_batches(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    expiring_soon: bool = Query(False, description="Filter batches expiring within 30 days"),
):
    """
    Retrieve a list of all inventory batches with product details.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **expiring_soon**: If true, only show batches expiring within 30 days
    """
    try:
        return await InventoryService.get_all_batches(
            skip=skip, limit=limit, expiring_soon=expiring_soon
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve inventory batches: {str(e)}",
        )


@router.get(
    "/expiring",
    response_model=List[InventoryBatchResponse],
    summary="Get expiring batches",
)
async def get_expiring_batches(
    days: int = Query(30, ge=1, le=365, description="Days threshold for expiry"),
):
    """
    Get inventory batches expiring within specified number of days.
    
    Useful for identifying products that need discount adjustments.
    """
    try:
        return await InventoryService.get_expiring_batches(days_threshold=days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve expiring batches: {str(e)}",
        )


@router.get(
    "/product/{product_id}",
    response_model=List[InventoryBatchResponse],
    summary="Get batches for a specific product",
)
async def get_product_batches(
    product_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    Get all inventory batches for a specific product.
    """
    # Verify product exists
    product = await ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    
    try:
        return await InventoryService.get_batches_by_product(
            product_id=product_id, skip=skip, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product batches: {str(e)}",
        )


@router.get(
    "/{batch_id}",
    response_model=InventoryBatchResponse,
    summary="Get batch by ID",
)
async def get_inventory_batch(batch_id: int):
    """
    Get a specific inventory batch by its ID.
    """
    batch = await InventoryService.get_batch_by_id(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory batch with ID {batch_id} not found",
        )
    return batch


@router.put(
    "/{batch_id}",
    response_model=InventoryBatchResponse,
    summary="Update an inventory batch",
)
async def update_inventory_batch(batch_id: int, batch: InventoryBatchUpdate):
    """
    Update an existing inventory batch. Only provided fields will be updated.
    """
    try:
        updated_batch = await InventoryService.update_batch(batch_id, batch)
        if not updated_batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory batch with ID {batch_id} not found",
            )
        return updated_batch
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update inventory batch: {str(e)}",
        )


@router.delete(
    "/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an inventory batch",
)
async def delete_inventory_batch(batch_id: int):
    """
    Delete an inventory batch by ID. This will also delete all associated discounts.
    """
    success = await InventoryService.delete_batch(batch_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory batch with ID {batch_id} not found",
        )


@router.patch(
    "/{batch_id}/quantity",
    response_model=InventoryBatchResponse,
    summary="Update batch quantity",
)
async def update_batch_quantity(
    batch_id: int,
    quantity_delta: int = Query(..., description="Quantity change (positive or negative)"),
):
    """
    Update batch quantity by a delta value.
    
    Use positive values to increase quantity, negative to decrease.
    Useful for tracking sales or stock adjustments.
    """
    try:
        updated_batch = await InventoryService.update_batch_quantity(
            batch_id=batch_id, quantity_delta=quantity_delta
        )
        if not updated_batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory batch with ID {batch_id} not found",
            )
        return updated_batch
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update batch quantity: {str(e)}",
        )
