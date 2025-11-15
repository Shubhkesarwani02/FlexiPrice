from typing import List
from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.discount import (
    DiscountCalculationRequest,
    DiscountCalculationResponse,
    BatchDiscountResponse,
)
from app.services.discount_service import DiscountService

router = APIRouter()


@router.post(
    "/compute/{batch_id}",
    response_model=DiscountCalculationResponse,
    summary="Compute discount for a specific batch",
)
async def compute_batch_discount(
    batch_id: int,
    use_ml: bool = Query(False, description="Use ML recommendation"),
):
    """
    Compute and save discount for a specific inventory batch.
    
    This applies the discount rules engine to calculate the optimal discount
    based on expiry date, quantity, and category.
    
    - **batch_id**: ID of the inventory batch
    - **use_ml**: Whether to use ML recommendations (future feature)
    """
    try:
        return await DiscountService.compute_and_save_discount(
            batch_id=batch_id,
            use_ml_recommendation=use_ml
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute discount: {str(e)}"
        )


@router.post(
    "/compute-all",
    response_model=List[DiscountCalculationResponse],
    summary="Compute discounts for all eligible batches",
)
async def compute_all_discounts(
    expiring_only: bool = Query(True, description="Only process expiring batches"),
    days_threshold: int = Query(30, ge=1, le=365, description="Days threshold for expiry"),
):
    """
    Compute and save discounts for all eligible inventory batches.
    
    This is typically run on a schedule to keep discounts up-to-date.
    
    - **expiring_only**: If true, only process batches expiring within threshold
    - **days_threshold**: Number of days threshold for expiry filtering
    """
    try:
        return await DiscountService.compute_all_batch_discounts(
            expiring_only=expiring_only,
            days_threshold=days_threshold
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute discounts: {str(e)}"
        )


@router.get(
    "/preview/{batch_id}",
    response_model=DiscountCalculationResponse,
    summary="Preview discount without saving",
)
async def preview_batch_discount(batch_id: int):
    """
    Preview what discount would be applied to a batch without saving.
    
    Useful for testing and UI previews.
    """
    try:
        return await DiscountService.preview_discount(batch_id=batch_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview discount: {str(e)}"
        )


@router.get(
    "/active/{batch_id}",
    response_model=BatchDiscountResponse,
    summary="Get active discount for a batch",
)
async def get_active_discount(batch_id: int):
    """
    Get the currently active discount for a batch.
    """
    discount = await DiscountService.get_active_discount(batch_id=batch_id)
    if not discount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active discount found for batch {batch_id}"
        )
    return discount


@router.get(
    "/history/{batch_id}",
    response_model=List[BatchDiscountResponse],
    summary="Get discount history for a batch",
)
async def get_discount_history(
    batch_id: int,
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
):
    """
    Get discount history for a batch, showing how discounts have changed over time.
    """
    try:
        return await DiscountService.get_batch_discount_history(
            batch_id=batch_id,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve discount history: {str(e)}"
        )
