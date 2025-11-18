"""
Model training module for NBA Predictor.
Handles data splitting, scaling, model training, and evaluation.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss, classification_report
import xgboost as xgb
import lightgbm as lgb
from src.config import (
    MODEL_ARTIFACTS_DIR, TRAIN_SEASONS, VAL_SEASON, TEST_SEASON
)
from src.feature_engineering import create_feature_set, calculate_elo_ratings
from src.database import get_session


# Feature columns (excluding metadata and targets)
FEATURE_COLUMNS = [
    'is_home',
    'team_elo',
    'opponent_elo',
    'elo_diff',
    'avg_pts_scored_l10',
    'avg_pts_allowed_l10',
    'avg_fg_pct_l10',
    'avg_tov_l10',
    'avg_plus_minus_l10',
    'avg_rebounds_l10',
    'avg_assists_l10',
    'opp_avg_pts_scored_l10',
    'opp_avg_pts_allowed_l10',
    'opp_avg_fg_pct_l10',
    'opp_avg_tov_l10',
    'opp_avg_plus_minus_l10',
    'h2h_win_pct',
    'days_since_last_game',
    'opponent_days_since_last_game',
    'rest_advantage'
]


def split_data_temporally(features_df: pd.DataFrame):
    """
    Split data temporally by season (not randomly).
    
    Returns:
        X_train, y_train, X_val, y_val, X_test, y_test
    """
    print("Splitting data temporally...")
    
    # Training set: specified seasons
    train_df = features_df[features_df['season'].isin(TRAIN_SEASONS)].copy()
    
    # Validation set: validation season
    val_df = features_df[features_df['season'] == VAL_SEASON].copy()
    
    # Test set: test season
    test_df = features_df[features_df['season'] == TEST_SEASON].copy()
    
    print(f"Train set: {len(train_df)} samples ({TRAIN_SEASONS[0]}-{TRAIN_SEASONS[-1]})")
    print(f"Validation set: {len(val_df)} samples ({VAL_SEASON})")
    print(f"Test set: {len(test_df)} samples ({TEST_SEASON})")
    
    # Extract features and targets
    X_train = train_df[FEATURE_COLUMNS].values
    y_train = train_df['target_did_win'].values
    
    X_val = val_df[FEATURE_COLUMNS].values
    y_val = val_df['target_did_win'].values
    
    X_test = test_df[FEATURE_COLUMNS].values
    y_test = test_df['target_did_win'].values
    
    return X_train, y_train, X_val, y_val, X_test, y_test


def scale_data(X_train, X_val, X_test):
    """
    Scale features using StandardScaler.
    Fit only on training data, transform all sets.
    
    Returns:
        X_train_scaled, X_val_scaled, X_test_scaled, scaler
    """
    print("Scaling data...")
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler
    scaler_path = MODEL_ARTIFACTS_DIR / "data_scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")
    
    return X_train_scaled, X_val_scaled, X_test_scaled, scaler


def train_models(X_train, y_train, X_val, y_val):
    """
    Train multiple models and select the best one.
    
    Returns:
        best_model, best_model_name, results_dict
    """
    print("Training models...")
    
    models = {}
    results = {}
    
    # Model 1: Logistic Regression (Baseline)
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    
    lr_val_pred = lr_model.predict(X_val)
    lr_val_proba = lr_model.predict_proba(X_val)
    lr_acc = accuracy_score(y_val, lr_val_pred)
    lr_logloss = log_loss(y_val, lr_val_proba)
    
    models['logistic_regression'] = lr_model
    results['logistic_regression'] = {
        'accuracy': lr_acc,
        'log_loss': lr_logloss
    }
    print(f"  Accuracy: {lr_acc:.4f}, Log Loss: {lr_logloss:.4f}")
    
    # Model 2: Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    rf_val_pred = rf_model.predict(X_val)
    rf_val_proba = rf_model.predict_proba(X_val)
    rf_acc = accuracy_score(y_val, rf_val_pred)
    rf_logloss = log_loss(y_val, rf_val_proba)
    
    models['random_forest'] = rf_model
    results['random_forest'] = {
        'accuracy': rf_acc,
        'log_loss': rf_logloss
    }
    print(f"  Accuracy: {rf_acc:.4f}, Log Loss: {rf_logloss:.4f}")
    
    # Model 3: XGBoost
    print("Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        early_stopping_rounds=20,
        verbose=False
    )
    
    xgb_val_pred = xgb_model.predict(X_val)
    xgb_val_proba = xgb_model.predict_proba(X_val)
    xgb_acc = accuracy_score(y_val, xgb_val_pred)
    xgb_logloss = log_loss(y_val, xgb_val_proba)
    
    models['xgboost'] = xgb_model
    results['xgboost'] = {
        'accuracy': xgb_acc,
        'log_loss': xgb_logloss
    }
    print(f"  Accuracy: {xgb_acc:.4f}, Log Loss: {xgb_logloss:.4f}")
    
    # Model 4: LightGBM
    print("Training LightGBM...")
    lgb_model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    lgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(stopping_rounds=20), lgb.log_evaluation(0)]
    )
    
    lgb_val_pred = lgb_model.predict(X_val)
    lgb_val_proba = lgb_model.predict_proba(X_val)
    lgb_acc = accuracy_score(y_val, lgb_val_pred)
    lgb_logloss = log_loss(y_val, lgb_val_proba)
    
    models['lightgbm'] = lgb_model
    results['lightgbm'] = {
        'accuracy': lgb_acc,
        'log_loss': lgb_logloss
    }
    print(f"  Accuracy: {lgb_acc:.4f}, Log Loss: {lgb_logloss:.4f}")
    
    # Select best model (lowest log loss)
    best_model_name = min(results.keys(), key=lambda k: results[k]['log_loss'])
    best_model = models[best_model_name]
    
    print(f"\nBest model: {best_model_name}")
    print(f"  Validation Accuracy: {results[best_model_name]['accuracy']:.4f}")
    print(f"  Validation Log Loss: {results[best_model_name]['log_loss']:.4f}")
    
    return best_model, best_model_name, results


def evaluate_model(model, X_test, y_test, model_name: str = "Model"):
    """
    Evaluate model on test set and print metrics.
    """
    print(f"\nEvaluating {model_name} on test set...")
    
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    logloss = log_loss(y_test, y_proba)
    
    print(f"Test Accuracy: {acc:.4f}")
    print(f"Test Log Loss: {logloss:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return {
        'accuracy': acc,
        'log_loss': logloss,
        'predictions': y_pred,
        'probabilities': y_proba
    }


def train_pipeline():
    """
    Complete training pipeline:
    1. Calculate ELO ratings
    2. Create feature set
    3. Split data temporally
    4. Scale data
    5. Train models
    6. Evaluate best model
    7. Save best model
    """
    print("=" * 60)
    print("NBA Predictor - Model Training Pipeline")
    print("=" * 60)
    
    db = get_session()
    try:
        # Step 1: Calculate ELO ratings
        print("\n[Step 1/6] Calculating ELO ratings...")
        calculate_elo_ratings(db)
        
        # Step 2: Create feature set
        print("\n[Step 2/6] Creating feature set...")
        features_df = create_feature_set(db)
        
        # Step 3: Split data
        print("\n[Step 3/6] Splitting data temporally...")
        X_train, y_train, X_val, y_val, X_test, y_test = split_data_temporally(features_df)
        
        # Step 4: Scale data
        print("\n[Step 4/6] Scaling data...")
        X_train_scaled, X_val_scaled, X_test_scaled, scaler = scale_data(
            X_train, X_val, X_test
        )
        
        # Step 5: Train models
        print("\n[Step 5/6] Training models...")
        best_model, best_model_name, results = train_models(
            X_train_scaled, y_train, X_val_scaled, y_val
        )
        
        # Step 6: Evaluate and save
        print("\n[Step 6/6] Evaluating best model and saving...")
        test_results = evaluate_model(best_model, X_test_scaled, y_test, best_model_name)
        
        # Save best model
        model_path = MODEL_ARTIFACTS_DIR / "best_model.joblib"
        joblib.dump(best_model, model_path)
        print(f"\nBest model saved to {model_path}")
        
        # Save feature columns for prediction
        feature_cols_path = MODEL_ARTIFACTS_DIR / "feature_columns.joblib"
        joblib.dump(FEATURE_COLUMNS, feature_cols_path)
        print(f"Feature columns saved to {feature_cols_path}")
        
        print("\n" + "=" * 60)
        print("Training pipeline complete!")
        print("=" * 60)
        
        return best_model, best_model_name, results, test_results
        
    finally:
        db.close()


if __name__ == "__main__":
    train_pipeline()

