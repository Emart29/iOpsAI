"""
API Router for dataset upload and management
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.upload_handler import process_upload_file
from storage import storage
from pathlib import Path

router = APIRouter(prefix="/api", tags=["datasets"])

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV file and create a new session"""
    return await process_upload_file(file, enhanced=False)

@router.get("/profile/{session_id}")
async def get_data_profile(session_id: str):
    """Get detailed profile of the dataset"""
    import pandas as pd
    
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        
        profile = []
        for col in df.columns:
            col_data = df[col]
            profile_item = {
                "column": col,
                "dtype": str(col_data.dtype),
                "non_null": int(col_data.count()),
                "unique": int(col_data.nunique()),
                "missing_pct": float((col_data.isna().sum() / len(df)) * 100)
            }
            
            # Numeric stats
            if col_data.dtype in ['int64', 'float64']:
                profile_item["stats"] = {
                    "mean": float(col_data.mean()) if not col_data.isna().all() else None,
                    "median": float(col_data.median()) if not col_data.isna().all() else None,
                    "std": float(col_data.std()) if not col_data.isna().all() else None,
                    "min": float(col_data.min()) if not col_data.isna().all() else None,
                    "max": float(col_data.max()) if not col_data.isna().all() else None,
                    "q1": float(col_data.quantile(0.25)) if not col_data.isna().all() else None,
                    "q3": float(col_data.quantile(0.75)) if not col_data.isna().all() else None,
                }
            else:
                # Categorical top values
                value_counts = col_data.value_counts().head(5)
                profile_item["top_values"] = [
                    {"value": str(val), "count": int(count)} 
                    for val, count in value_counts.items()
                ]
            
            profile.append(profile_item)
        
        return profile
    except Exception as e:
        raise HTTPException(500, f"Error profiling data: {str(e)}")