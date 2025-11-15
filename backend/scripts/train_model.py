"""
XGBoost Model Training Script
Trains a binary classification model to predict purchase probability.

Features:
- Data loading and preprocessing
- Feature engineering
- Train/validation/test split
- XGBoost training with hyperparameter tuning
- Model evaluation with comprehensive metrics
- Feature importance analysis
- Model persistence

Usage:
    python3 scripts/train_model.py data/synthetic_purchases.csv
    python3 scripts/train_model.py data/synthetic_purchases.csv --tune
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)
from sklearn.preprocessing import LabelEncoder
import joblib


def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    """Load CSV data and perform initial preparation."""
    print(f"\n{'='*70}")
    print("LOADING DATA")
    print('='*70)
    print(f"Loading data from {filepath}...")
    
    df = pd.read_csv(filepath)
    print(f"✓ Loaded {len(df):,} records")
    print(f"✓ Features: {len(df.columns)} columns")
    print(f"✓ Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create additional engineered features."""
    print(f"\n{'='*70}")
    print("FEATURE ENGINEERING")
    print('='*70)
    
    # Create copy to avoid modifying original
    df = df.copy()
    
    # 1. Urgency score (combination of expiry and inventory)
    df['urgency_score'] = (
        (1 / (df['days_to_expiry'] + 1)) * 10 +  # Expiry urgency
        (1 / (df['inventory_level'] + 1)) * 100   # Scarcity
    )
    
    # 2. Price tiers
    df['price_tier'] = pd.cut(
        df['base_price'],
        bins=[0, 5, 15, 100],
        labels=['low', 'medium', 'high']
    )
    
    # 3. Discount effectiveness (discount relative to days to expiry)
    df['discount_per_day'] = df['discount_pct'] / (df['days_to_expiry'] + 1)
    
    # 4. Inventory risk (low inventory near expiry)
    df['inventory_risk'] = (df['inventory_level'] < 20) & (df['days_to_expiry'] < 7)
    df['inventory_risk'] = df['inventory_risk'].astype(int)
    
    # 5. High urgency flag
    df['high_urgency'] = (df['days_to_expiry'] <= 3).astype(int)
    
    # 6. Deep discount flag
    df['deep_discount'] = (df['discount_pct'] >= 30).astype(int)
    
    # 7. Interaction: discount × expiry
    df['discount_expiry_interaction'] = df['discount_pct'] * (1 / (df['days_to_expiry'] + 1))
    
    # 8. Price discount ratio
    df['price_discount_ratio'] = df['discount_pct'] / (df['base_price'] + 1)
    
    print(f"✓ Created 8 engineered features")
    print(f"  - urgency_score: Expiry + scarcity combined")
    print(f"  - price_tier: Low/medium/high")
    print(f"  - discount_per_day: Discount effectiveness")
    print(f"  - inventory_risk: Low stock + near expiry")
    print(f"  - high_urgency: ≤3 days to expiry")
    print(f"  - deep_discount: ≥30% discount")
    print(f"  - discount_expiry_interaction: Combined effect")
    print(f"  - price_discount_ratio: Relative discount")
    
    return df


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str], Dict]:
    """Prepare feature matrix and target variable."""
    print(f"\n{'='*70}")
    print("PREPARING FEATURES")
    print('='*70)
    
    # Define feature columns
    numeric_features = [
        'base_price',
        'discount_pct',
        'days_to_expiry',
        'inventory_level',
        'day_of_week',
        'month',
        'is_weekend',
        'is_summer',
        'is_winter',
        'is_holiday_season',
        'season_multiplier',
        'urgency_score',
        'discount_per_day',
        'inventory_risk',
        'high_urgency',
        'deep_discount',
        'discount_expiry_interaction',
        'price_discount_ratio',
    ]
    
    categorical_features = ['category', 'price_tier']
    
    # Encode categorical features
    label_encoders = {}
    df_encoded = df.copy()
    
    for cat_feature in categorical_features:
        le = LabelEncoder()
        df_encoded[cat_feature + '_encoded'] = le.fit_transform(df_encoded[cat_feature])
        label_encoders[cat_feature] = le
        print(f"✓ Encoded {cat_feature}: {len(le.classes_)} categories")
    
    # Final feature list
    feature_columns = numeric_features + [f + '_encoded' for f in categorical_features]
    
    # Prepare X and y
    X = df_encoded[feature_columns]
    y = df_encoded['sold']
    
    print(f"\n✓ Feature matrix shape: {X.shape}")
    print(f"✓ Target distribution: {y.value_counts().to_dict()}")
    print(f"✓ Positive class rate: {y.mean()*100:.2f}%")
    
    return X, y, feature_columns, label_encoders


def split_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, val_size: float = 0.1):
    """Split data into train, validation, and test sets."""
    print(f"\n{'='*70}")
    print("SPLITTING DATA")
    print('='*70)
    
    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Second split: separate validation from training
    val_size_adjusted = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size_adjusted, random_state=42, stratify=y_temp
    )
    
    print(f"✓ Train set:      {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"✓ Validation set: {len(X_val):,} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"✓ Test set:       {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    print(f"\nClass distribution:")
    print(f"  Train:      {y_train.mean()*100:.2f}% positive")
    print(f"  Validation: {y_val.mean()*100:.2f}% positive")
    print(f"  Test:       {y_test.mean()*100:.2f}% positive")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    params: Dict = None,
    num_boost_round: int = 100
) -> xgb.Booster:
    """Train XGBoost model."""
    print(f"\n{'='*70}")
    print("TRAINING XGBOOST MODEL")
    print('='*70)
    
    # Default parameters
    if params is None:
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 1,
            'seed': 42
        }
    
    print("Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # Create DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    
    # Training with early stopping
    evals = [(dtrain, 'train'), (dval, 'validation')]
    evals_result = {}
    
    print(f"\nTraining for up to {num_boost_round} rounds...")
    start_time = time.time()
    
    bst = xgb.train(
        params,
        dtrain,
        num_boost_round=num_boost_round,
        evals=evals,
        early_stopping_rounds=10,
        evals_result=evals_result,
        verbose_eval=20
    )
    
    train_time = time.time() - start_time
    
    print(f"\n✓ Training completed in {train_time:.2f} seconds")
    print(f"✓ Best iteration: {bst.best_iteration}")
    print(f"✓ Best score: {bst.best_score:.4f}")
    
    return bst, evals_result


def evaluate_model(
    model: xgb.Booster,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    feature_names: List[str]
) -> Dict:
    """Evaluate model performance."""
    print(f"\n{'='*70}")
    print("MODEL EVALUATION")
    print('='*70)
    
    # Predictions
    dtest = xgb.DMatrix(X_test)
    y_pred_proba = model.predict(dtest)
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\nClassification Metrics:")
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {roc_auc:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"                Predicted")
    print(f"              Not Sold  Sold")
    print(f"Actual Not Sold   {cm[0][0]:4d}   {cm[0][1]:4d}")
    print(f"       Sold       {cm[1][0]:4d}   {cm[1][1]:4d}")
    
    # Classification report
    print(f"\n{classification_report(y_test, y_pred, target_names=['Not Sold', 'Sold'])}")
    
    # Feature importance
    print(f"\nTop 10 Most Important Features:")
    importance_dict = model.get_score(importance_type='gain')
    importance_sorted = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    
    for i, (feature, importance) in enumerate(importance_sorted[:10], 1):
        # XGBoost uses actual feature names in newer versions
        feature_name = feature
        print(f"  {i:2d}. {feature_name:30s} {importance:8.2f}")
    
    # Return metrics
    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc),
        'confusion_matrix': cm.tolist(),
        'feature_importance': {k: float(v) for k, v in importance_sorted[:20]}
    }
    
    return metrics


def save_model_and_artifacts(
    model: xgb.Booster,
    metrics: Dict,
    feature_names: List[str],
    label_encoders: Dict,
    output_dir: str = "models"
):
    """Save trained model and associated artifacts."""
    print(f"\n{'='*70}")
    print("SAVING MODEL")
    print('='*70)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = f"{output_dir}/xgb_recommend.json"
    model.save_model(model_path)
    print(f"✓ Saved model: {model_path}")
    
    # Save feature names
    feature_path = f"{output_dir}/feature_names.json"
    with open(feature_path, 'w') as f:
        json.dump(feature_names, f, indent=2)
    print(f"✓ Saved features: {feature_path}")
    
    # Save label encoders
    encoder_path = f"{output_dir}/label_encoders.pkl"
    joblib.dump(label_encoders, encoder_path)
    print(f"✓ Saved encoders: {encoder_path}")
    
    # Save metrics
    metrics_path = f"{output_dir}/metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✓ Saved metrics: {metrics_path}")
    
    # Save model info
    info = {
        'model_type': 'XGBoost Binary Classifier',
        'target': 'Purchase Probability (sold)',
        'num_features': len(feature_names),
        'features': feature_names,
        'training_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'performance': {
            'accuracy': metrics['accuracy'],
            'roc_auc': metrics['roc_auc'],
            'f1_score': metrics['f1_score']
        }
    }
    
    info_path = f"{output_dir}/model_info.json"
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=2)
    print(f"✓ Saved info: {info_path}")
    
    print(f"\n✓ All artifacts saved to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(
        description="Train XGBoost model for purchase prediction"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input CSV file path"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models",
        help="Output directory for model files (default: models)"
    )
    parser.add_argument(
        "--num-rounds",
        type=int,
        default=100,
        help="Number of boosting rounds (default: 100)"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test set size (default: 0.2)"
    )
    parser.add_argument(
        "--val-size",
        type=float,
        default=0.1,
        help="Validation set size (default: 0.1)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("XGBOOST PURCHASE PREDICTION MODEL TRAINING")
    print("="*70)
    
    # Load data
    df = load_and_prepare_data(args.input)
    
    # Engineer features
    df = engineer_features(df)
    
    # Prepare features
    X, y, feature_names, label_encoders = prepare_features(df)
    
    # Split data
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        X, y, test_size=args.test_size, val_size=args.val_size
    )
    
    # Train model
    model, evals_result = train_xgboost(
        X_train, y_train, X_val, y_val, num_boost_round=args.num_rounds
    )
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, feature_names)
    
    # Save model and artifacts
    save_model_and_artifacts(model, metrics, feature_names, label_encoders, args.output_dir)
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"\n✓ Model ready for deployment!")
    print(f"✓ Test Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"✓ Test ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"\nNext steps:")
    print(f"  1. Review model performance in {args.output_dir}/metrics.json")
    print(f"  2. Load model: bst = xgb.Booster(); bst.load_model('{args.output_dir}/xgb_recommend.json')")
    print(f"  3. Make predictions: predictions = bst.predict(xgb.DMatrix(X_new))")
    print(f"  4. Integrate into API service")


if __name__ == "__main__":
    main()
