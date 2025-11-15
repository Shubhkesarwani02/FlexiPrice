from typing import List
from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.discount import (
    DiscountCalculationRequest,
    DiscountCalculationResponse,
    BatchDiscountResponse,
)
from app.services.discount_service import DiscountService

router = APIRouter()


@router.get(
    "",
    response_model=List[BatchDiscountResponse],
    summary="Get all active discounts",
)
async def get_all_discounts(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of discounts to return"),
    active_only: bool = Query(True, description="Return only active discounts"),
):
    """
    Get all batch discounts in the system.
    
    - **limit**: Maximum number of discounts to return
    - **active_only**: If true, returns only currently active discounts
    """
    try:
        return await DiscountService.get_all_discounts(limit=limit, active_only=active_only)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve discounts: {str(e)}"
        )


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


@router.post(
    "/trigger-recompute",
    summary="Manually trigger discount recomputation",
)
async def trigger_discount_recompute(
    days_threshold: int = Query(30, ge=1, le=365, description="Process batches expiring within N days"),
    async_task: bool = Query(True, description="Run as background task"),
):
    """
    Manually trigger discount recomputation for all eligible batches.
    
    This endpoint allows manual triggering of the discount calculation process
    that normally runs on a schedule.
    
    - **days_threshold**: Only process batches expiring within this many days
    - **async_task**: If true, run as Celery background task; if false, run synchronously
    
    Returns task ID if async, or results if synchronous.
    """
    try:
        if async_task:
            # Import here to avoid circular dependencies
            from app.tasks import recompute_all_discounts
            
            # Queue the task
            task = recompute_all_discounts.delay(days_threshold=days_threshold)
            
            return {
                "status": "queued",
                "task_id": task.id,
                "message": f"Discount recomputation queued for batches expiring within {days_threshold} days"
            }
        else:
            # Run synchronously (for testing/small datasets)
            result = await DiscountService.compute_all_batch_discounts(
                expiring_only=True,
                days_threshold=days_threshold
            )
            
            return {
                "status": "completed",
                "results": result,
                "message": "Discount recomputation completed"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger recomputation: {str(e)}"
        )


@router.get(
    "/task-status/{task_id}",
    summary="Check status of background task",
)
async def get_task_status(task_id: str):
    """
    Check the status of a background discount computation task.
    
    - **task_id**: The Celery task ID returned by trigger-recompute
    """
    try:
        from app.celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": task.state,
            "ready": task.ready(),
        }
        
        if task.ready():
            if task.successful():
                response["result"] = task.result
            else:
                response["error"] = str(task.info)
        else:
            response["info"] = str(task.info) if task.info else None
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check task status: {str(e)}"
        )
