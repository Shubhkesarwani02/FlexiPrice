"""
ML Admin Endpoints
Provides ML-powered discount recommendations for admin users.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status

from app.services.ml_predictor import ml_predictor
from pydantic import BaseModel, Field


router = APIRouter()


class DiscountRecommendation(BaseModel):
    """Discount recommendation with uplift metrics."""
    product_id: str
    category: str
    base_price: float
    days_to_expiry: int
    inventory_level: int
    discount_pct: float
    discounted_price: float
    purchase_probability: float
    baseline_probability: float
    uplift: float
    uplift_pct: float
    expected_revenue: float
    confidence: str


class RecommendationResponse(BaseModel):
    """Response containing discount recommendations."""
    recommendations: List[DiscountRecommendation]
    model_info: dict


@router.get(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Get ML-powered discount recommendations",
)
async def recommend_discounts(
    product_id: str = Query(..., description="Product SKU"),
    days_to_expiry: int = Query(..., ge=1, description="Days until product expires"),
    inventory: int = Query(..., ge=1, description="Current inventory level"),
    top_k: int = Query(3, ge=1, le=10, description="Number of recommendations to return"),
    min_discount: float = Query(10.0, ge=0, le=50, description="Minimum discount percentage"),
    max_discount: float = Query(50.0, ge=0, le=100, description="Maximum discount percentage"),
    discount_step: float = Query(5.0, ge=1, le=10, description="Discount step size"),
):
    """
    Get ML-powered discount recommendations for a product.
    
    Returns top-k discount options with:
    - Purchase probability at each discount level
    - Uplift compared to baseline (no discount)
    - Expected revenue calculation
    - Confidence level
    
    **Example usage:**
    ```
    GET /admin/ml/recommend?product_id=DAI-00123&days_to_expiry=3&inventory=10
    ```
    
    **Returns:**
    - Top 3 discount recommendations ranked by purchase probability
    - Each recommendation includes uplift metrics
    - Baseline probability for comparison
    """
    try:
        # Initialize ML predictor if needed
        if not ml_predictor._initialized:
            if not ml_predictor.initialize():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="ML model not available. Please train and deploy model first."
                )
        
        # Validate discount range
        if min_discount >= max_discount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_discount must be less than max_discount"
            )
        
        # Generate recommendations
        recommendations = await ml_predictor.recommend_discounts(
            product_id=product_id,
            days_to_expiry=days_to_expiry,
            inventory_level=inventory,
            top_k=top_k,
            discount_range=(min_discount, max_discount),
            discount_step=discount_step
        )
        
        # Get model info
        model_info = ml_predictor.get_model_info()
        
        return {
            "recommendations": recommendations,
            "model_info": model_info
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get(
    "/model-info",
    summary="Get ML model information",
)
async def get_model_info():
    """
    Get information about the deployed ML model.
    
    Returns:
    - Model type and architecture
    - Number of features
    - Training date
    - Performance metrics
    - Initialization status
    """
    try:
        if not ml_predictor._initialized:
            ml_predictor.initialize()
        
        return ml_predictor.get_model_info()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.post(
    "/predict",
    summary="Predict purchase probability",
)
async def predict_purchase_probability(
    product_id: str = Query(..., description="Product SKU"),
    discount_pct: float = Query(..., ge=0, le=100, description="Discount percentage"),
    days_to_expiry: int = Query(..., ge=1, description="Days until expiration"),
    inventory: int = Query(..., ge=1, description="Inventory level"),
):
    """
    Predict purchase probability for a specific product and discount combination.
    
    **Example usage:**
    ```
    POST /admin/ml/predict?product_id=SEA-00123&discount_pct=35&days_to_expiry=2&inventory=5
    ```
    
    **Returns:**
    - Purchase probability (0-1)
    - Confidence level
    - Product context
    """
    try:
        # Initialize ML predictor if needed
        if not ml_predictor._initialized:
            if not ml_predictor.initialize():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="ML model not available"
                )
        
        # Fetch product
        from app.core.database import prisma
        from datetime import datetime
        
        product = await prisma.product.findUnique(where={"sku": product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        # Prepare features
        now = datetime.now()
        day_of_week = now.weekday()
        month = now.month
        
        features = {
            'base_price': float(product.basePrice),
            'category': product.category,
            'discount_pct': discount_pct,
            'days_to_expiry': days_to_expiry,
            'inventory_level': inventory,
            'day_of_week': day_of_week,
            'month': month,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'is_summer': 1 if month in [6, 7, 8] else 0,
            'is_winter': 1 if month in [12, 1, 2] else 0,
            'is_holiday_season': 1 if month in [11, 12] else 0,
            'season_multiplier': ml_predictor._get_season_multiplier(product.category, month)
        }
        
        # Predict
        probability = ml_predictor.predict_probability(features)
        confidence = ml_predictor._get_confidence_level(probability)
        
        return {
            "product_id": product_id,
            "discount_pct": discount_pct,
            "purchase_probability": round(probability, 4),
            "confidence": confidence,
            "context": {
                "base_price": float(product.basePrice),
                "category": product.category,
                "days_to_expiry": days_to_expiry,
                "inventory_level": inventory,
                "discounted_price": round(float(product.basePrice) * (1 - discount_pct / 100), 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
