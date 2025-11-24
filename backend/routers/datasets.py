from storage import storage
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pandas as pd
import numpy as np
import uuid
import aiofiles
import os
import io
from datetime import datetime
from typing import Dict, Any

from deps import get_sessions, get_datasets
from utils.data_processing import generate_data_profile

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    sessions: dict = Depends(get_sessions),
    datasets: dict = Depends(get_datasets)
):
    """Upload and process dataset"""
    try:
        print(f"Received file: {file.filename}, Content-Type: {file.content_type}")
        
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        valid_extensions = ['.csv', '.xlsx', '.xls']
        if not any(file.filename.lower().endswith(ext) for ext in valid_extensions):
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel file.")
        
        # Read file contents
        contents = await file.read()
        print(f"File size: {len(contents)} bytes")
        
        # Validate file size (100MB limit)
        if len(contents) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB.")
        
        # Process file based on type
        if file.filename.lower().endswith('.csv'):
            try:
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
        else:  # Excel files
            try:
                df = pd.read_excel(io.BytesIO(contents))  # Fixed: Added missing )
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")
        
        print(f"DataFrame loaded: {df.shape}")
        
        # Generate IDs
        session_id = str(uuid.uuid4())
        dataset_id = str(uuid.uuid4())
        
        # Store dataset metadata
        datasets[dataset_id] = {
            'filename': file.filename,
            'uploaded_at': datetime.now().isoformat(),
            'session_id': session_id,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        # Create uploads directory if it doesn't exist
        os.makedirs("data/uploads", exist_ok=True)
        file_path = f"data/uploads/{dataset_id}.parquet"
        
        # Save dataframe as parquet
        df.to_parquet(file_path)
        
        # Generate initial profile
        profile = generate_data_profile(df)
        
        # Store session
        sessions[session_id] = {
            'dataset_id': dataset_id,
            'created_at': datetime.now().isoformat(),
            'analyses': [],
            'file_path': file_path,
            'profile': profile
        }
        
        # Store initial analysis
        sessions[session_id]['analyses'].append({
            'type': 'initial_profile',
            'timestamp': datetime.now().isoformat(),
            'results': profile
        })
        
        return {
            "session_id": session_id,
            "dataset_id": dataset_id,
            "profile": profile,
            "message": "Dataset uploaded and processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/{dataset_id}")
async def get_dataset_info(
    dataset_id: str,
    datasets: dict = Depends(get_datasets)
):
    """Get dataset metadata"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return datasets[dataset_id]

@router.get("/{dataset_id}/sample")
async def get_dataset_sample(
    dataset_id: str, 
    rows: int = 10,
    sessions: dict = Depends(get_sessions),
    datasets: dict = Depends(get_datasets)
):
    """Get sample data from dataset"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session_id = datasets[dataset_id]['session_id']
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = sessions[session_id]['file_path']
    
    try:
        # Read only the first n rows for efficiency
        df = pd.read_parquet(file_path)
        sample_df = df.head(rows)
        
        return {
            "columns": list(sample_df.columns),
            "data": sample_df.replace({np.nan: None}).to_dict('records'),
            "total_rows": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")