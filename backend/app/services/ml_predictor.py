"""
ML Predictor Service
Loads trained XGBoost model and provides discount recommendations.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

try:
    import xgboost as xgb
    import pandas as pd
    import joblib
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available. ML predictions disabled.")

from app.core.database import prisma


logger = logging.getLogger(__name__)


class MLPredictor:
    """ML model predictor for purchase probability and discount recommendations."""
    
    def __init__(self):
        self.model: Optional[xgb.Booster] = None
        self.feature_names: Optional[List[str]] = None
        self.label_encoders: Optional[Dict] = None
        self.model_info: Optional[Dict] = None
        self._initialized = False
        
        # Model paths
        self.model_dir = Path(__file__).parent.parent.parent / "models"
        self.model_path = self.model_dir / "xgb_recommend.json"
        self.features_path = self.model_dir / "feature_names.json"
        self.encoders_path = self.model_dir / "label_encoders.pkl"
        self.info_path = self.model_dir / "model_info.json"
    
    def initialize(self) -> bool:
        """Load model and artifacts."""
        if self._initialized:
            return True
        
        if not XGBOOST_AVAILABLE:
            logger.error("XGBoost not available. Cannot initialize ML predictor.")
            return False
        
        try:
            # Check if model exists
            if not self.model_path.exists():
                logger.warning(f"Model not found at {self.model_path}")
                return False
            
            # Load model
            self.model = xgb.Booster()
            self.model.load_model(str(self.model_path))
            logger.info(f"Loaded model from {self.model_path}")
            
            # Load feature names
            with open(self.features_path, 'r') as f:
                self.feature_names = json.load(f)
            
            # Load label encoders
            self.label_encoders = joblib.load(self.encoders_path)
            
            # Load model info
            with open(self.info_path, 'r') as f:
                self.model_info = json.load(f)
            
            self._initialized = True
            logger.info("ML predictor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ML predictor: {e}")
            return False
    
    def _engineer_features(self, data: Dict) -> Dict:
        """Add engineered features to input data."""
        # Make a copy
        features = data.copy()
        
        # Urgency score
        features['urgency_score'] = (
            (1 / (features['days_to_expiry'] + 1)) * 10 +
            (1 / (features['inventory_level'] + 1)) * 100
        )
        
        # Price tier
        if features['base_price'] <= 5:
            features['price_tier'] = 'low'
        elif features['base_price'] <= 15:
            features['price_tier'] = 'medium'
        else:
            features['price_tier'] = 'high'
        
        # Discount per day
        features['discount_per_day'] = features['discount_pct'] / (features['days_to_expiry'] + 1)
        
        # Inventory risk
        features['inventory_risk'] = int(
            features['inventory_level'] < 20 and features['days_to_expiry'] < 7
        )
        
        # High urgency
        features['high_urgency'] = int(features['days_to_expiry'] <= 3)
        
        # Deep discount
        features['deep_discount'] = int(features['discount_pct'] >= 30)
        
        # Discount expiry interaction
        features['discount_expiry_interaction'] = (
            features['discount_pct'] * (1 / (features['days_to_expiry'] + 1))
        )
        
        # Price discount ratio
        features['price_discount_ratio'] = features['discount_pct'] / (features['base_price'] + 1)
        
        return features
    
    def _prepare_input(self, data: Dict) -> pd.DataFrame:
        """Prepare input for model prediction."""
        if not self._initialized:
            raise RuntimeError("ML predictor not initialized")
        
        # Engineer features
        features = self._engineer_features(data)
        
        # Encode categorical features
        features['category_encoded'] = self.label_encoders['category'].transform(
            [features['category']]
        )[0]
        features['price_tier_encoded'] = self.label_encoders['price_tier'].transform(
            [features['price_tier']]
        )[0]
        
        # Create DataFrame with correct feature order
        df = pd.DataFrame([features])
        return df[self.feature_names]
    
    def predict_probability(self, data: Dict) -> float:
        """Predict purchase probability for given input."""
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize ML predictor")
        
        try:
            X = self._prepare_input(data)
            dmatrix = xgb.DMatrix(X)
            probability = float(self.model.predict(dmatrix)[0])
            return probability
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_probabilities_batch(self, data_list: List[Dict]) -> List[float]:
        """Predict purchase probabilities for multiple inputs."""
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize ML predictor")
        
        try:
            # Prepare all inputs
            dfs = [self._prepare_input(data) for data in data_list]
            X = pd.concat(dfs, ignore_index=True)
            
            dmatrix = xgb.DMatrix(X)
            probabilities = self.model.predict(dmatrix)
            return [float(p) for p in probabilities]
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise
    
    async def recommend_discounts(
        self,
        product_id: str,
        days_to_expiry: int,
        inventory_level: int,
        top_k: int = 3,
        discount_range: Tuple[float, float] = (10.0, 50.0),
        discount_step: float = 5.0
    ) -> List[Dict]:
        """
        Recommend top-k discount options with expected uplift.
        
        Args:
            product_id: Product SKU
            days_to_expiry: Days until product expires
            inventory_level: Current inventory level
            top_k: Number of recommendations to return
            discount_range: Min and max discount percentages to test
            discount_step: Step size for discount testing
            
        Returns:
            List of discount recommendations with probabilities and uplift
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize ML predictor")
        
        try:
            # Fetch product details
            product = await prisma.product.findUnique(where={"sku": product_id})
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            # Get current date info
            now = datetime.now()
            day_of_week = now.weekday()
            month = now.month
            
            # Prepare base features
            base_features = {
                'base_price': float(product.basePrice),
                'category': product.category,
                'days_to_expiry': days_to_expiry,
                'inventory_level': inventory_level,
                'day_of_week': day_of_week,
                'month': month,
                'is_weekend': 1 if day_of_week >= 5 else 0,
                'is_summer': 1 if month in [6, 7, 8] else 0,
                'is_winter': 1 if month in [12, 1, 2] else 0,
                'is_holiday_season': 1 if month in [11, 12] else 0,
                'season_multiplier': self._get_season_multiplier(product.category, month)
            }
            
            # Test different discount levels
            discount_levels = []
            current = discount_range[0]
            while current <= discount_range[1]:
                discount_levels.append(current)
                current += discount_step
            
            # Predict probability for each discount level
            test_data = []
            for discount in discount_levels:
                features = base_features.copy()
                features['discount_pct'] = discount
                test_data.append(features)
            
            probabilities = self.predict_probabilities_batch(test_data)
            
            # Calculate baseline (no discount)
            baseline_features = base_features.copy()
            baseline_features['discount_pct'] = 0.0
            baseline_prob = self.predict_probability(baseline_features)
            
            # Create recommendations with uplift
            recommendations = []
            for discount, probability in zip(discount_levels, probabilities):
                uplift = probability - baseline_prob
                uplift_pct = (uplift / baseline_prob * 100) if baseline_prob > 0 else 0
                
                # Calculate expected revenue
                discounted_price = float(product.basePrice) * (1 - discount / 100)
                expected_revenue = discounted_price * probability * inventory_level
                
                recommendations.append({
                    'discount_pct': round(discount, 1),
                    'purchase_probability': round(probability, 4),
                    'uplift': round(uplift, 4),
                    'uplift_pct': round(uplift_pct, 2),
                    'expected_revenue': round(expected_revenue, 2),
                    'discounted_price': round(discounted_price, 2),
                    'confidence': self._get_confidence_level(probability)
                })
            
            # Sort by probability and return top-k
            recommendations.sort(key=lambda x: x['purchase_probability'], reverse=True)
            top_recommendations = recommendations[:top_k]
            
            # Add context
            for rec in top_recommendations:
                rec['baseline_probability'] = round(baseline_prob, 4)
                rec['product_id'] = product_id
                rec['days_to_expiry'] = days_to_expiry
                rec['inventory_level'] = inventory_level
                rec['base_price'] = float(product.basePrice)
                rec['category'] = product.category
            
            return top_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise
    
    def _get_season_multiplier(self, category: str, month: int) -> float:
        """Get seasonality multiplier for category and month."""
        # Seasonal patterns by category
        seasonal_patterns = {
            'Seafood': [0.8, 0.7, 0.9, 1.0, 1.1, 1.3, 1.4, 1.3, 1.0, 0.9, 0.8, 0.9],
            'Produce': [0.8, 0.7, 0.9, 1.0, 1.1, 1.3, 1.4, 1.3, 1.0, 0.9, 0.8, 0.9],
            'Beverages': [0.9, 0.9, 1.0, 1.0, 1.05, 1.1, 1.15, 1.1, 1.0, 1.0, 0.95, 1.0],
            'Frozen': [0.9, 0.9, 1.0, 1.0, 1.05, 1.1, 1.15, 1.1, 1.0, 1.0, 0.95, 1.0],
            'Dairy': [1.0] * 12,
            'Bakery': [1.0] * 12,
            'Meat': [1.0] * 12,
            'Snacks': [1.0] * 12,
        }
        
        pattern = seasonal_patterns.get(category, [1.0] * 12)
        return pattern[month - 1]
    
    def _get_confidence_level(self, probability: float) -> str:
        """Get confidence level based on probability."""
        if probability >= 0.7:
            return "high"
        elif probability >= 0.5:
            return "medium"
        elif probability >= 0.3:
            return "low"
        else:
            return "very_low"
    
    def get_model_info(self) -> Dict:
        """Get model metadata."""
        if not self._initialized:
            if not self.initialize():
                return {"error": "Model not initialized"}
        
        return {
            "model_type": self.model_info.get("model_type", "XGBoost"),
            "num_features": self.model_info.get("num_features", 0),
            "training_date": self.model_info.get("training_date"),
            "performance": self.model_info.get("performance", {}),
            "initialized": self._initialized
        }


# Singleton instance
ml_predictor = MLPredictor()
