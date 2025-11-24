from storage import storage
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
import numpy as np
from typing import Dict, Any

from deps import get_sessions
from utils.data_processing import generate_data_profile, detect_outliers, generate_correlations

router = APIRouter(prefix="/eda", tags=["exploratory data analysis"])

@router.post("/profile")
async def profile_data(
    session_id: str,
    sessions: dict = Depends(get_sessions)
):
    """Generate comprehensive data profile"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        file_path = sessions[session_id]['file_path']
        df = pd.read_parquet(file_path)
        profile = generate_data_profile(df)
        
        sessions[session_id]['analyses'].append({
            'type': 'profile',
            'timestamp': datetime.now().isoformat(),
            'results': profile
        })
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating profile: {str(e)}")

@router.post("/outliers")
async def detect_data_outliers(
    session_id: str, 
    method: str = "iqr",
    sessions: dict = Depends(get_sessions)
):
    """Detect outliers in numeric columns"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = sessions[session_id]['file_path']
    
    try:
        df = pd.read_parquet(file_path)
        outliers = detect_outliers(df, method)
        
        sessions[session_id]['analyses'].append({
            'type': 'outlier_detection',
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'results': outliers
        })
        
        return outliers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting outliers: {str(e)}")

@router.post("/correlations")
async def get_correlations(
    session_id: str,
    sessions: dict = Depends(get_sessions)
):
    """Calculate correlation matrix for numeric columns"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = sessions[session_id]['file_path']
    
    try:
        df = pd.read_parquet(file_path)
        correlations = generate_correlations(df)
        
        sessions[session_id]['analyses'].append({
            'type': 'correlation_analysis',
            'timestamp': datetime.now().isoformat(),
            'results': correlations
        })
        
        return correlations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating correlations: {str(e)}")

@router.post("/summary")
async def get_dataset_summary(
    session_id: str,
    sessions: dict = Depends(get_sessions)
):
    """Get comprehensive dataset summary"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = sessions[session_id]['file_path']
    
    try:
        df = pd.read_parquet(file_path)
        
        # Basic info
        basic_info = {
            "shape": df.shape,
            "memory_usage": int(df.memory_usage(deep=True).sum()),
            "missing_values": df.isnull().sum().sum(),
            "duplicate_rows": df.duplicated().sum()
        }
        
        # Column types
        column_types = {
            "numeric": len(df.select_dtypes(include=[np.number]).columns),
            "categorical": len(df.select_dtypes(include=['object']).columns),
            "datetime": len(df.select_dtypes(include=['datetime']).columns),
            "boolean": len(df.select_dtypes(include=['bool']).columns)
        }
        
        # Quality metrics
        quality_metrics = {
            "completeness": float(1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))),
            "uniqueness": float(df.nunique().mean() / df.shape[0]),
            "data_quality_score": calculate_data_quality_score(df)
        }
        
        summary = {
            "basic_info": basic_info,
            "column_types": column_types,
            "quality_metrics": quality_metrics,
            "columns": list(df.columns)
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

def calculate_data_quality_score(df):
    """Calculate overall data quality score"""
    try:
        # Completeness score
        completeness = 1 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))
        
        # Uniqueness score (avoid completely unique ID columns)
        uniqueness = df.nunique().mean() / df.shape[0]
        uniqueness = min(uniqueness, 0.95)  # Cap to avoid perfect scores for ID columns
        
        # Consistency score (check for mixed types)
        consistency = 1.0
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column has mixed types
                unique_types = set(type(x) for x in df[col].dropna())
                if len(unique_types) > 1:
                    consistency *= 0.8
        
        return (completeness * 0.4 + uniqueness * 0.3 + consistency * 0.3) * 100
        
    except:
        return 0.0