"""
A/B Testing Analytics Endpoints
Provides comparative analytics for ML vs rule-based recommendations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
from pathlib import Path

from app.schemas.experiment import (
    ExperimentGroup,
    ExperimentMetric,
    ExperimentSummary,
    ExperimentComparison,
)
from app.services.ab_test_service import ab_test_service

router = APIRouter()


def generate_mock_experiment_metrics(
    experiment_group: ExperimentGroup,
    num_products: int = 10
) -> List[ExperimentMetric]:
    """
    Generate mock experiment metrics based on synthetic data patterns.
    
    This simulates what would come from real DB metrics.
    In production, query actual experiment_metrics table.
    """
    data_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "synthetic_purchases.csv"
    
    if not data_path.exists():
        raise HTTPException(status_code=503, detail="Data not found")
    
    df = pd.read_csv(data_path)
    
    # Simulate different performance for control vs ML
    if experiment_group == ExperimentGroup.CONTROL:
        # Rule-based: moderate performance
        conversion_multiplier = 0.35  # 35% base conversion
        discount_avg = 25.0
    else:
        # ML: better performance
        conversion_multiplier = 0.42  # 42% conversion (20% lift)
        discount_avg = 28.5
    
    metrics = []
    period_start = datetime.utcnow() - timedelta(days=7)
    period_end = datetime.utcnow()
    
    # Sample products
    unique_products = df.drop_duplicates('product_id').head(num_products)
    
    for idx, row in unique_products.iterrows():
        # Simulate metrics
        impressions = int(100 + (idx % 50) * 10)  # 100-600 impressions per product
        conversions = int(impressions * conversion_multiplier)
        units_sold = conversions * 2  # Average 2 units per conversion
        
        revenue = float(row['base_price']) * (1 - discount_avg/100) * units_sold
        
        metrics.append(ExperimentMetric(
            id=idx + 1,
            product_id=idx + 1,
            experiment_group=experiment_group,
            impressions=impressions,
            conversions=conversions,
            revenue=Decimal(str(round(revenue, 2))),
            units_sold=units_sold,
            avg_discount_pct=Decimal(str(discount_avg)),
            conversion_rate=Decimal(str(round(conversions / impressions * 100, 2))),
            period_start=period_start,
            period_end=period_end
        ))
    
    return metrics


@router.get("/comparison", response_model=ExperimentComparison)
async def get_experiment_comparison(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Compare ML variant vs control group performance.
    
    Returns:
    - Summary for both groups
    - Lift calculations (% improvement)
    - Statistical significance indicators
    """
    try:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)
        
        # Get metrics for both groups
        control_metrics = generate_mock_experiment_metrics(ExperimentGroup.CONTROL, num_products=10)
        ml_metrics = generate_mock_experiment_metrics(ExperimentGroup.ML_VARIANT, num_products=10)
        
        # Calculate summaries
        control_summary = ab_test_service.calculate_experiment_summary(control_metrics)
        ml_summary = ab_test_service.calculate_experiment_summary(ml_metrics)
        
        # Compare
        comparison = ab_test_service.compare_experiments(
            control_summary=control_summary,
            ml_summary=ml_summary,
            period_start=period_start,
            period_end=period_end
        )
        
        return comparison
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate comparison: {str(e)}")


@router.get("/metrics/{experiment_group}", response_model=List[ExperimentMetric])
async def get_experiment_metrics(
    experiment_group: ExperimentGroup,
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get detailed metrics for a specific experiment group.
    
    Returns per-product metrics including:
    - Impressions, conversions, revenue
    - Conversion rates
    - Average discount applied
    """
    try:
        metrics = generate_mock_experiment_metrics(experiment_group, num_products=10)
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/summary/{experiment_group}", response_model=ExperimentSummary)
async def get_experiment_summary(
    experiment_group: ExperimentGroup,
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get aggregated summary for a specific experiment group.
    """
    try:
        metrics = generate_mock_experiment_metrics(experiment_group, num_products=10)
        summary = ab_test_service.calculate_experiment_summary(metrics)
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.get("/winning-variant")
async def get_winning_variant(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze"),
    metric: str = Query(default="conversion_rate", description="Metric to compare: conversion_rate, revenue, units")
):
    """
    Determine which experiment variant is performing better.
    
    Returns the winning group and confidence level.
    """
    try:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)
        
        # Get metrics
        control_metrics = generate_mock_experiment_metrics(ExperimentGroup.CONTROL, num_products=10)
        ml_metrics = generate_mock_experiment_metrics(ExperimentGroup.ML_VARIANT, num_products=10)
        
        # Calculate summaries
        control_summary = ab_test_service.calculate_experiment_summary(control_metrics)
        ml_summary = ab_test_service.calculate_experiment_summary(ml_metrics)
        
        # Compare based on metric
        if metric == "conversion_rate":
            control_value = float(control_summary.conversion_rate)
            ml_value = float(ml_summary.conversion_rate)
            unit = "%"
        elif metric == "revenue":
            control_value = float(control_summary.revenue_per_product)
            ml_value = float(ml_summary.revenue_per_product)
            unit = "$"
        elif metric == "units":
            control_value = control_summary.total_units_sold / control_summary.total_products
            ml_value = ml_summary.total_units_sold / ml_summary.total_products
            unit = "units"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown metric: {metric}")
        
        # Determine winner
        if ml_value > control_value:
            winner = ExperimentGroup.ML_VARIANT
            improvement = ((ml_value - control_value) / control_value * 100)
            message = f"ML variant is winning by {improvement:.1f}%"
        elif control_value > ml_value:
            winner = ExperimentGroup.CONTROL
            improvement = ((control_value - ml_value) / ml_value * 100)
            message = f"Control is winning by {improvement:.1f}%"
        else:
            winner = None
            improvement = 0.0
            message = "Both variants performing equally"
        
        # Simple confidence (in production, use proper statistical tests)
        sample_size = control_summary.total_impressions + ml_summary.total_impressions
        if sample_size < 100:
            confidence = "low"
        elif sample_size < 500:
            confidence = "medium"
        else:
            confidence = "high"
        
        return {
            "winner": winner,
            "metric": metric,
            "control_value": control_value,
            "ml_variant_value": ml_value,
            "improvement_pct": improvement,
            "confidence": confidence,
            "sample_size": sample_size,
            "message": message,
            "recommendation": (
                "Continue experiment" if confidence != "high"
                else f"Consider rolling out {winner.value if winner else 'current approach'}"
            )
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to determine winner: {str(e)}")
