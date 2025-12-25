"""
AutoML API Router for iOps Data Copilot
Provides endpoints for automated machine learning
"""

from fastapi import APIRouter, HTTPException, Body
from storage import storage
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from utils.automl import AutoMLEngine, hyperparameter_tuning_optuna
import json
from datetime import datetime

router = APIRouter(prefix="/api/ml", tags=["automl"])


@router.post("/train/{session_id}")
async def train_models(
    session_id: str,
    config: Dict[str, Any] = Body(...)
):
    """
    Train multiple ML models and compare performance
    
    Request body:
    {
        "target_column": "column_name",
        "task_type": "classification" or "regression",
        "test_size": 0.2,
        "models": ["all"] or ["Random Forest", "XGBoost", ...]
    }
    """
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        # Load data
        df = pd.read_parquet(session["parquet_path"])
        
        # Get configuration
        target_column = config.get("target_column")
        task_type = config.get("task_type", "classification")
        test_size = config.get("test_size", 0.2)
        
        if not target_column or target_column not in df.columns:
            raise HTTPException(400, f"Invalid target column: {target_column}")
        
        # Initialize AutoML engine
        engine = AutoMLEngine(task_type=task_type)
        
        # Prepare data
        X_train, X_test, y_train, y_test = engine.prepare_data(df, target_column, test_size)
        
        # Train all models
        results = engine.train_all_models(X_train, X_test, y_train, y_test)
        
        # Get feature importance for best model
        feature_importance = engine.get_feature_importance()
        
        # Save best model
        model_dir = Path(session["parquet_path"]).parent / "models" / session_id
        model_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "session_id": session_id,
            "target_column": target_column,
            "task_type": task_type,
            "test_size": test_size,
            "feature_names": engine.feature_names,
            "trained_at": datetime.now().isoformat(),
            "best_score": engine.best_score
        }
        
        engine.save_model(engine.best_model, model_dir, metadata)
        
        # Format results for response
        model_results = {}
        for name, result in results.items():
            if result['status'] == 'success':
                model_results[name] = {
                    'metrics': result['metrics'],
                    'status': 'success'
                }
            else:
                model_results[name] = {
                    'status': 'failed',
                    'error': result.get('error', 'Unknown error')
                }
        
        return {
            "message": "Models trained successfully",
            "results": model_results,
            "feature_importance": feature_importance[:10],  # Top 10 features
            "best_model": max(model_results.items(), 
                            key=lambda x: x[1]['metrics'].get('accuracy' if task_type == 'classification' else 'r2_score', 0) 
                            if x[1]['status'] == 'success' else 0)[0],
            "model_saved": True
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error training models: {str(e)}")


@router.post("/tune/{session_id}")
async def tune_hyperparameters(
    session_id: str,
    config: Dict[str, Any] = Body(...)
):
    """
    Perform hyperparameter tuning for a specific model
    
    Request body:
    {
        "target_column": "column_name",
        "task_type": "classification" or "regression",
        "model_name": "Random Forest" or "XGBoost",
        "n_trials": 50
    }
    """
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        # Load data
        df = pd.read_parquet(session["parquet_path"])
        
        # Get configuration
        target_column = config.get("target_column")
        task_type = config.get("task_type", "classification")
        model_name = config.get("model_name", "Random Forest")
        n_trials = config.get("n_trials", 50)
        
        if not target_column or target_column not in df.columns:
            raise HTTPException(400, f"Invalid target column: {target_column}")
        
        # Initialize AutoML engine
        engine = AutoMLEngine(task_type=task_type)
        
        # Prepare data
        X_train, X_test, y_train, y_test = engine.prepare_data(df, target_column, 0.2)
        
        # Perform hyperparameter tuning
        tuning_results = hyperparameter_tuning_optuna(
            model_name, X_train, y_train, task_type, n_trials
        )
        
        return {
            "message": f"Hyperparameter tuning complete for {model_name}",
            "model_name": model_name,
            "best_params": tuning_results.get("best_params", {}),
            "best_score": tuning_results.get("best_score"),
            "n_trials": n_trials
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error tuning hyperparameters: {str(e)}")


@router.post("/predict/{session_id}")
async def make_predictions(
    session_id: str,
    data: Dict[str, Any] = Body(...)
):
    """
    Make predictions using trained model
    
    Request body:
    {
        "features": {...} or "use_test_data": true
    }
    """
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        # Load model
        model_dir = Path(session["parquet_path"]).parent / "models" / session_id
        if not model_dir.exists():
            raise HTTPException(404, "No trained model found for this session")
        
        # Load metadata
        metadata_file = model_dir / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        task_type = metadata.get("task_type", "classification")
        target_column = metadata.get("target_column")
        
        # Initialize engine and load model
        engine = AutoMLEngine(task_type=task_type)
        engine.load_model(model_dir)
        
        # Get prediction data
        if data.get("use_test_data"):
            # Use test portion of original data
            df = pd.read_parquet(session["parquet_path"])
            X = df.drop(columns=[target_column])
            y_true = df[target_column].values if target_column in df.columns else None
        else:
            # Use provided features
            features = data.get("features", {})
            X = pd.DataFrame([features])
            y_true = None
        
        # Make predictions
        predictions = engine.predict(X)
        
        return {
            "predictions": predictions.tolist(),
            "n_samples": len(predictions),
            "model_info": {
                "task_type": task_type,
                "target_column": target_column,
                "trained_at": metadata.get("trained_at")
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error making predictions: {str(e)}")


@router.get("/models/{session_id}")
async def list_models(session_id: str):
    """List all trained models for a session"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        model_dir = Path(session["parquet_path"]).parent / "models" / session_id
        
        if not model_dir.exists():
            return {"models": []}
        
        # Load metadata
        metadata_file = model_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return {
                "models": [{
                    "session_id": session_id,
                    "target_column": metadata.get("target_column"),
                    "task_type": metadata.get("task_type"),
                    "trained_at": metadata.get("trained_at"),
                    "best_score": metadata.get("best_score"),
                    "feature_count": len(metadata.get("feature_names", []))
                }]
            }
        
        return {"models": []}
        
    except Exception as e:
        raise HTTPException(500, f"Error listing models: {str(e)}")


@router.get("/feature-importance/{session_id}")
async def get_feature_importance(session_id: str):
    """Get feature importance from trained model"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        model_dir = Path(session["parquet_path"]).parent / "models" / session_id
        if not model_dir.exists():
            raise HTTPException(404, "No trained model found")
        
        # Load metadata
        metadata_file = model_dir / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        task_type = metadata.get("task_type", "classification")
        
        # Load model
        engine = AutoMLEngine(task_type=task_type)
        engine.load_model(model_dir)
        engine.feature_names = metadata.get("feature_names", [])
        
        # Get feature importance
        importance = engine.get_feature_importance()
        
        return {
            "feature_importance": importance,
            "n_features": len(importance)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error getting feature importance: {str(e)}")


@router.delete("/models/{session_id}")
async def delete_model(session_id: str):
    """Delete trained model for a session"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        model_dir = Path(session["parquet_path"]).parent / "models" / session_id
        
        if model_dir.exists():
            import shutil
            shutil.rmtree(model_dir)
            return {"message": "Model deleted successfully"}
        else:
            raise HTTPException(404, "No model found to delete")
            
    except Exception as e:
        raise HTTPException(500, f"Error deleting model: {str(e)}")


@router.get("/available-models")
async def get_available_models():
    """Get list of available ML algorithms"""
    return {
        "classification": [
            "Logistic Regression",
            "Random Forest",
            "Decision Tree",
            "Gradient Boosting",
            "XGBoost",
            "LightGBM"
        ],
        "regression": [
            "Linear Regression",
            "Ridge",
            "Lasso",
            "Random Forest",
            "Decision Tree",
            "Gradient Boosting",
            "XGBoost",
            "LightGBM"
        ]
    }
