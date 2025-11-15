"""
A/B Testing API Endpoints
Manage experiments and get recommendations based on experiment groups.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
from pathlib import Path

from app.schemas.experiment import (
    ExperimentGroup,
    ExperimentAssignment,
    ExperimentAssignRequest,
    ExperimentMetric,
    ExperimentSummary,
    ExperimentComparison,
    RecommendationRequest,
    RecommendationResponse,
    ProductWithExperiment,
)
from app.services.ab_test_service import ab_test_service
from app.services.ml_predictor import ml_predictor

router = APIRouter()


@router.get("", response_model=List[ProductWithExperiment])
async def list_all_experiments(
    group_filter: Optional[str] = Query(None, description="Filter by experiment group: CONTROL or ML_VARIANT")
):
    """
    List all products enrolled in experiments.
    
    Returns products with their experiment assignments and current status.
    """
    try:
        from app.core.database import prisma
        
        # Build where clause - Prisma Python uses isNot for NOT NULL checks
        if group_filter:
            where_clause = {
                "experimentGroup": group_filter
            }
        else:
            # Get all products (return empty list if none have experiments)
            where_clause = {}
        
        products = await prisma.product.find_many(
            where=where_clause,
            include={"inventoryBatches": True}
        )
        
        # Filter in Python if no group_filter to only show products with experiments
        if not group_filter:
            products = [p for p in products if p.experimentGroup is not None]
        
        return [
            ProductWithExperiment(
                id=p.id,
                sku=p.sku,
                name=p.name,
                category=p.category or "Unknown",
                base_price=float(p.basePrice),
                experiment_group=p.experimentGroup,
                experiment_assigned_at=p.experimentAssignedAt
            )
            for p in products
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list experiments: {str(e)}"
        )


# Mock database functions (replace with actual Prisma calls in production)
def get_mock_products() -> List[dict]:
    """Load products from synthetic data."""
    data_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "synthetic_purchases.csv"
    
    if not data_path.exists():
        raise HTTPException(status_code=503, detail="Data not found")
    
    df = pd.read_csv(data_path)
    
    # Get unique products
    products = []
    for idx, row in df.drop_duplicates('product_id').head(50).iterrows():
        products.append({
            "id": idx + 1,
            "sku": row['product_id'],
            "name": f"{row['category']} Product",
            "category": row['category'],
            "base_price": float(row['base_price']),
            "experiment_group": None,
            "experiment_assigned_at": None
        })
    
    return products


def get_mock_product(product_id: int) -> Optional[dict]:
    """Get single product by ID."""
    products = get_mock_products()
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# In-memory storage for experiments (replace with DB in production)
experiment_assignments = {}
experiment_metrics_store = []


@router.post("/assign", response_model=List[ExperimentAssignment])
async def assign_experiments(request: ExperimentAssignRequest):
    """
    Assign products to an experiment group.
    
    This sets the experiment_group field on products to either:
    - CONTROL: Uses rule-based discount logic
    - ML_VARIANT: Uses ML-recommended discounts
    """
    try:
        products = get_mock_products()
        
        # Filter to requested products
        target_products = [p for p in products if p["id"] in request.product_ids]
        
        if not target_products:
            raise HTTPException(status_code=404, detail="No matching products found")
        
        # Assign experiment group
        assignments = []
        now = datetime.utcnow()
        
        for product in target_products:
            product["experiment_group"] = request.experiment_group.value
            product["experiment_assigned_at"] = now
            
            # Store assignment
            experiment_assignments[product["id"]] = {
                "experiment_group": request.experiment_group,
                "assigned_at": now
            }
            
            assignments.append(ExperimentAssignment(
                product_id=product["id"],
                sku=product["sku"],
                experiment_group=request.experiment_group,
                assigned_at=now
            ))
        
        return assignments
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign experiments: {str(e)}")


@router.post("/assign/random")
async def assign_random(
    split_ratio: float = Query(default=0.5, ge=0.1, le=0.9, description="Fraction for control group")
):
    """
    Randomly split all products into control and ML variant groups.
    
    Args:
        split_ratio: Fraction to assign to control (default 0.5 = 50/50 split)
    """
    try:
        products = get_mock_products()
        product_ids = [p["id"] for p in products]
        
        # Random split
        assignment_map = ab_test_service.random_assignment(product_ids, split_ratio)
        
        # Apply assignments
        all_assignments = []
        now = datetime.utcnow()
        
        for group, ids in assignment_map.items():
            for prod_id in ids:
                experiment_assignments[prod_id] = {
                    "experiment_group": group,
                    "assigned_at": now
                }
                
                product = get_mock_product(prod_id)
                if product:
                    all_assignments.append(ExperimentAssignment(
                        product_id=prod_id,
                        sku=product["sku"],
                        experiment_group=group,
                        assigned_at=now
                    ))
        
        return {
            "message": f"Assigned {len(all_assignments)} products",
            "control_count": len(assignment_map[ExperimentGroup.CONTROL]),
            "ml_variant_count": len(assignment_map[ExperimentGroup.ML_VARIANT]),
            "assignments": all_assignments
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign random: {str(e)}")


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """
    Get discount recommendation based on product's experiment group.
    
    - CONTROL group: Uses rule-based logic
    - ML_VARIANT group: Uses ML model predictions
    - Unassigned: Defaults to CONTROL
    """
    try:
        # Get product
        product = get_mock_product(request.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get experiment assignment
        assignment = experiment_assignments.get(request.product_id)
        experiment_group = (
            assignment["experiment_group"] if assignment 
            else ExperimentGroup.CONTROL
        )
        
        # Get recommendation based on group
        if experiment_group == ExperimentGroup.ML_VARIANT:
            # ML recommendation
            ml_predictor.initialize()
            recommendation = ab_test_service.get_ml_recommendation(
                ml_predictor=ml_predictor,
                product_id=request.product_id,
                days_to_expiry=request.days_to_expiry,
                inventory=request.inventory,
                top_k=request.top_k
            )
            
            return RecommendationResponse(
                product_id=request.product_id,
                experiment_group=ExperimentGroup.ML_VARIANT,
                recommended_discount_pct=Decimal(str(recommendation["discount_pct"])),
                expected_probability=(
                    Decimal(str(recommendation["probability"])) 
                    if recommendation.get("probability") else None
                ),
                method=recommendation["method"],
                reason=recommendation["reason"]
            )
        else:
            # Rule-based recommendation
            recommendation = ab_test_service.get_rule_based_recommendation(
                base_price=product["base_price"],
                days_to_expiry=request.days_to_expiry,
                inventory=request.inventory,
                category=product.get("category")
            )
            
            return RecommendationResponse(
                product_id=request.product_id,
                experiment_group=ExperimentGroup.CONTROL,
                recommended_discount_pct=Decimal(str(recommendation["discount_pct"])),
                expected_probability=None,
                method=recommendation["method"],
                reason=recommendation["reason"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {str(e)}")


@router.get("/assignments", response_model=List[ProductWithExperiment])
async def list_assignments():
    """
    List all products with their experiment group assignments.
    """
    try:
        products = get_mock_products()
        
        result = []
        for product in products:
            assignment = experiment_assignments.get(product["id"])
            
            result.append(ProductWithExperiment(
                id=product["id"],
                sku=product["sku"],
                name=product["name"],
                category=product.get("category"),
                base_price=Decimal(str(product["base_price"])),
                experiment_group=(
                    assignment["experiment_group"] if assignment else None
                ),
                experiment_assigned_at=(
                    assignment["assigned_at"] if assignment else None
                )
            ))
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list assignments: {str(e)}")


@router.get("/status")
async def experiment_status():
    """
    Get current experiment status and statistics.
    """
    try:
        control_count = sum(
            1 for a in experiment_assignments.values()
            if a["experiment_group"] == ExperimentGroup.CONTROL
        )
        
        ml_count = sum(
            1 for a in experiment_assignments.values()
            if a["experiment_group"] == ExperimentGroup.ML_VARIANT
        )
        
        total_products = len(get_mock_products())
        unassigned_count = total_products - len(experiment_assignments)
        
        return {
            "total_products": total_products,
            "assigned_products": len(experiment_assignments),
            "unassigned_products": unassigned_count,
            "control_count": control_count,
            "ml_variant_count": ml_count,
            "experiment_active": len(experiment_assignments) > 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.delete("/reset")
async def reset_experiments():
    """
    Reset all experiment assignments (for testing).
    """
    global experiment_assignments, experiment_metrics_store
    
    experiment_assignments.clear()
    experiment_metrics_store.clear()
    
    return {"message": "All experiments reset"}
