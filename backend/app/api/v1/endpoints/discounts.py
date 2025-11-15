from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.discount import (
    DiscountCalculationRequest,
    DiscountCalculationResponse,
    BatchDiscountResponse,
)
from app.services.discount_service import DiscountService

router = APIRouter()


@router.post(
    "/calculate",
    response_model=DiscountCalculationResponse,
    summary="Calculate discount for a batch",
)
async def calculate_discount(request: DiscountCalculationRequest):
    """
    Calculate the optimal discount for a specific inventory batch.
    
    This endpoint computes the discount based on:
    - Days to expiry
    - Current inventory quantity
    - Product category
    - Configured discount rules
    
    Does not persist the discount to the database.
    """
    try:
        return await DiscountService.calculate_batch_discount(
            batch_id=request.batch_id,
            use_ml_recommendation=request.use_ml_recommendation,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate discount: {str(e)}",
        )


@router.post(
    "/apply/{batch_id}",
    response_model=BatchDiscountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate and apply discount to batch",
)
async def apply_discount(
    batch_id: int,
    use_ml: bool = Query(False, description="Use ML recommendation"),
):
    """
    Calculate and persist discount for a batch.
    
    This endpoint:
    1. Calculates the optimal discount
    2. Saves it to the database
    3. Returns the discount record
    """
    try:
        return await DiscountService.apply_discount_to_batch(
            batch_id=batch_id,
            use_ml_recommendation=use_ml,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply discount: {str(e)}",
        )


@router.post(
    "/calculate-all",
    response_model=List[DiscountCalculationResponse],
    summary="Calculate discounts for all expiring batches",
)
async def calculate_all_discounts(
    days_threshold: int = Query(30, ge=1, le=365, description="Days until expiry threshold"),
    auto_apply: bool = Query(False, description="Automatically save discounts to database"),
):
    """
    Calculate discounts for all batches expiring within the threshold.
    
    Use this for:
    - Preview discounts before applying
    - Batch discount calculations
    - Scheduled discount updates
    
    Set `auto_apply=true` to automatically save discounts.
    """
    try:
        return await DiscountService.calculate_all_expiring_discounts(
            days_threshold=days_threshold,
            auto_apply=auto_apply,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate discounts: {str(e)}",
        )


@router.get(
    "/batch/{batch_id}/active",
    response_model=Optional[BatchDiscountResponse],
    summary="Get active discount for batch",
)
async def get_active_discount(batch_id: int):
    """
    Get the currently active discount for a batch.
    
    Returns the most recent discount that hasn't expired yet.
    """
    try:
        discount = await DiscountService.get_active_discount_for_batch(batch_id)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active discount found for batch {batch_id}",
            )
        return discount
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve discount: {str(e)}",
        )


@router.delete(
    "/{discount_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate a discount",
)
async def invalidate_discount(discount_id: int):
    """
    Mark a discount as invalid by setting its expiry to now.
    
    This effectively removes the discount from active use.
    """
    success = await DiscountService.invalidate_discount(discount_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discount with ID {discount_id} not found",
        )
