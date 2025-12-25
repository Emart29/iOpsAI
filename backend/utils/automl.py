"""
AutoML utilities for iOps Data Copilot
Supports classification and regression with automated model selection and hyperparameter tuning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import joblib
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
from datetime import datetime

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False


class AutoMLEngine:
    """Automated Machine Learning Engine"""
    
    def __init__(self, task_type: str = 'classification'):
        """
        Initialize AutoML Engine
        
        Args:
            task_type: 'classification' or 'regression'
        """
        self.task_type = task_type
        self.models = self._get_default_models()
        self.best_model = None
        self.best_score = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.target_name = None
        
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default models based on task type"""
        if self.task_type == 'classification':
            models = {
                'Logistic Regression': LogisticRegression(max_iter=1000),
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'Decision Tree': DecisionTreeClassifier(random_state=42),
                'Gradient Boosting': GradientBoostingClassifier(random_state=42),
            }
            if XGBOOST_AVAILABLE:
                models['XGBoost'] = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
            if LIGHTGBM_AVAILABLE:
                models['LightGBM'] = lgb.LGBMClassifier(random_state=42, verbose=-1)
        else:  # regression
            models = {
                'Linear Regression': LinearRegression(),
                'Ridge': Ridge(),
                'Lasso': Lasso(),
                'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'Decision Tree': DecisionTreeRegressor(random_state=42),
                'Gradient Boosting': GradientBoostingRegressor(random_state=42),
            }
            if XGBOOST_AVAILABLE:
                models['XGBoost'] = xgb.XGBRegressor(random_state=42)
            if LIGHTGBM_AVAILABLE:
                models['LightGBM'] = lgb.LGBMRegressor(random_state=42, verbose=-1)
        
        return models
    
    def prepare_data(self, df: pd.DataFrame, target_column: str, test_size: float = 0.2) -> Tuple:
        """
        Prepare data for training
        
        Args:
            df: Input DataFrame
            target_column: Name of target column
            test_size: Proportion of test set
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        self.feature_names = list(X.columns)
        self.target_name = target_column
        
        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
        
        # Encode target if classification
        if self.task_type == 'classification':
            y = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        return X_train, X_test, y_train, y_test
    
    def train_all_models(self, X_train, X_test, y_train, y_test) -> Dict[str, Dict]:
        """
        Train all models and compare performance
        
        Returns:
            Dictionary with model results
        """
        results = {}
        
        for name, model in self.models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                if self.task_type == 'classification':
                    metrics = {
                        'accuracy': float(accuracy_score(y_test, y_pred)),
                        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
                    }
                    # Try to calculate AUC if binary classification
                    if len(np.unique(y_test)) == 2:
                        try:
                            y_pred_proba = model.predict_proba(X_test)[:, 1]
                            metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba))
                        except:
                            metrics['roc_auc'] = None
                else:  # regression
                    metrics = {
                        'mse': float(mean_squared_error(y_test, y_pred)),
                        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                        'mae': float(mean_absolute_error(y_test, y_pred)),
                        'r2_score': float(r2_score(y_test, y_pred)),
                    }
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                metrics['cv_mean'] = float(cv_scores.mean())
                metrics['cv_std'] = float(cv_scores.std())
                
                results[name] = {
                    'model': model,
                    'metrics': metrics,
                    'status': 'success'
                }
                
            except Exception as e:
                results[name] = {
                    'model': None,
                    'metrics': {},
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Find best model
        if self.task_type == 'classification':
            best_name = max(results.items(), 
                          key=lambda x: x[1]['metrics'].get('accuracy', 0) if x[1]['status'] == 'success' else 0)[0]
            self.best_score = results[best_name]['metrics']['accuracy']
        else:
            best_name = min(results.items(), 
                          key=lambda x: x[1]['metrics'].get('rmse', float('inf')) if x[1]['status'] == 'success' else float('inf'))[0]
            self.best_score = results[best_name]['metrics']['rmse']
        
        self.best_model = results[best_name]['model']
        
        return results
    
    def get_feature_importance(self, model_name: str = None) -> List[Dict]:
        """Get feature importance for tree-based models"""
        model = self.best_model if model_name is None else self.models.get(model_name)
        
        if model is None or not hasattr(model, 'feature_importances_'):
            return []
        
        importances = model.feature_importances_
        feature_importance = [
            {
                'feature': self.feature_names[i],
                'importance': float(importances[i])
            }
            for i in range(len(importances))
        ]
        
        # Sort by importance
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return feature_importance
    
    def save_model(self, model, save_path: Path, metadata: Dict = None):
        """Save trained model and metadata"""
        # Save model
        model_file = save_path / 'model.joblib'
        joblib.dump(model, model_file)
        
        # Save scaler
        scaler_file = save_path / 'scaler.joblib'
        joblib.dump(self.scaler, scaler_file)
        
        # Save label encoder if classification
        if self.task_type == 'classification':
            encoder_file = save_path / 'label_encoder.joblib'
            joblib.dump(self.label_encoder, encoder_file)
        
        # Save metadata
        if metadata:
            metadata_file = save_path / 'metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
    
    def load_model(self, load_path: Path):
        """Load trained model and metadata"""
        model_file = load_path / 'model.joblib'
        scaler_file = load_path / 'scaler.joblib'
        
        self.best_model = joblib.load(model_file)
        self.scaler = joblib.load(scaler_file)
        
        if self.task_type == 'classification':
            encoder_file = load_path / 'label_encoder.joblib'
            if encoder_file.exists():
                self.label_encoder = joblib.load(encoder_file)
        
        # Load metadata
        metadata_file = load_path / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with best model"""
        if self.best_model is None:
            raise ValueError("No model trained yet")
        
        # Prepare features
        X_prepared = X.copy()
        categorical_cols = X_prepared.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X_prepared[col] = le.fit_transform(X_prepared[col].astype(str))
        
        # Scale
        X_scaled = self.scaler.transform(X_prepared)
        
        # Predict
        predictions = self.best_model.predict(X_scaled)
        
        # Decode if classification
        if self.task_type == 'classification':
            predictions = self.label_encoder.inverse_transform(predictions)
        
        return predictions


def hyperparameter_tuning_optuna(model_name: str, X_train, y_train, task_type: str, n_trials: int = 50) -> Dict:
    """
    Perform hyperparameter tuning using Optuna
    
    Args:
        model_name: Name of the model to tune
        X_train: Training features
        y_train: Training target
        task_type: 'classification' or 'regression'
        n_trials: Number of optimization trials
        
    Returns:
        Best parameters and score
    """
    if not OPTUNA_AVAILABLE:
        return {"error": "Optuna not available"}
    
    def objective(trial):
        if model_name == 'Random Forest':
            if task_type == 'classification':
                model = RandomForestClassifier(
                    n_estimators=trial.suggest_int('n_estimators', 50, 300),
                    max_depth=trial.suggest_int('max_depth', 3, 20),
                    min_samples_split=trial.suggest_int('min_samples_split', 2, 20),
                    min_samples_leaf=trial.suggest_int('min_samples_leaf', 1, 10),
                    random_state=42
                )
            else:
                model = RandomForestRegressor(
                    n_estimators=trial.suggest_int('n_estimators', 50, 300),
                    max_depth=trial.suggest_int('max_depth', 3, 20),
                    min_samples_split=trial.suggest_int('min_samples_split', 2, 20),
                    min_samples_leaf=trial.suggest_int('min_samples_leaf', 1, 10),
                    random_state=42
                )
        
        elif model_name == 'XGBoost' and XGBOOST_AVAILABLE:
            if task_type == 'classification':
                model = xgb.XGBClassifier(
                    n_estimators=trial.suggest_int('n_estimators', 50, 300),
                    max_depth=trial.suggest_int('max_depth', 3, 10),
                    learning_rate=trial.suggest_float('learning_rate', 0.01, 0.3),
                    subsample=trial.suggest_float('subsample', 0.6, 1.0),
                    colsample_bytree=trial.suggest_float('colsample_bytree', 0.6, 1.0),
                    random_state=42,
                    eval_metric='logloss'
                )
            else:
                model = xgb.XGBRegressor(
                    n_estimators=trial.suggest_int('n_estimators', 50, 300),
                    max_depth=trial.suggest_int('max_depth', 3, 10),
                    learning_rate=trial.suggest_float('learning_rate', 0.01, 0.3),
                    subsample=trial.suggest_float('subsample', 0.6, 1.0),
                    colsample_bytree=trial.suggest_float('colsample_bytree', 0.6, 1.0),
                    random_state=42
                )
        else:
            return 0
        
        # Cross-validation
        scores = cross_val_score(model, X_train, y_train, cv=5, 
                                scoring='accuracy' if task_type == 'classification' else 'neg_mean_squared_error')
        return scores.mean()
    
    # Create study
    study = optuna.create_study(direction='maximize' if task_type == 'classification' else 'maximize')
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    
    return {
        'best_params': study.best_params,
        'best_score': float(study.best_value),
        'n_trials': n_trials
    }
