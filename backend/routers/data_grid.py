from fastapi import APIRouter, HTTPException, Body
from storage import storage
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
import json

router = APIRouter(prefix="/api", tags=["data"])

@router.get("/data-preview/{session_id}")
async def get_data_preview(session_id: str, limit: int = 100):
    """Get a preview of the dataset for the data grid"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        
        # Limit rows for preview
        preview_df = df.head(limit)
        
        # Convert to records (list of dicts)
        rows = preview_df.to_dict('records')
        
        # Handle NaN values for JSON serialization
        for row in rows:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
        
        return {
            "rows": rows,
            "total_rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    except Exception as e:
        raise HTTPException(500, f"Error loading data preview: {str(e)}")

@router.post("/data-update/{session_id}")
async def update_data(session_id: str, updates: Dict[str, Any] = Body(...)):
    """Update data in the grid (for manual edits)"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        
        # Get updated rows from request
        updated_rows = updates.get("rows", [])
        
        if not updated_rows:
            raise HTTPException(400, "No rows provided for update")
        
        # Create new DataFrame from updated rows
        df_updated = pd.DataFrame(updated_rows)
        
        # Ensure column types match original
        for col in df.columns:
            if col in df_updated.columns:
                try:
                    df_updated[col] = df_updated[col].astype(df[col].dtype)
                except:
                    pass  # Keep original type if conversion fails
        
        # Save updated data to a new file
        updated_path = Path(session["parquet_path"]).parent / f"{session_id}_edited.parquet"
        df_updated.to_parquet(updated_path)
        
        # Also save as CSV for download
        csv_path = Path(session["parquet_path"]).parent / f"{session_id}_edited.csv"
        df_updated.to_csv(csv_path, index=False)
        
        return {
            "message": "Data updated successfully",
            "rows_updated": len(df_updated),
            "download_url": f"/api/download-edited/{session_id}"
        }
    except Exception as e:
        raise HTTPException(500, f"Error updating data: {str(e)}")

@router.get("/download-edited/{session_id}")
async def download_edited_data(session_id: str):
    """Download manually edited dataset"""
    from fastapi.responses import FileResponse
    
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    csv_path = Path(session["parquet_path"]).parent / f"{session_id}_edited.csv"
    if not csv_path.exists():
        raise HTTPException(404, "Edited file not found")
    
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename=f"edited_data_{session_id}.csv"
    )

@router.post("/transform/{session_id}")
async def apply_transformation(session_id: str, transformation: Dict[str, Any] = Body(...)):
    """Apply advanced transformations to data"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        
        transform_type = transformation.get("type")
        column = transformation.get("column")
        params = transformation.get("params", {})
        
        if transform_type == "convert_type":
            # Convert column data type
            target_type = params.get("target_type")
            if target_type == "numeric":
                df[column] = pd.to_numeric(df[column], errors='coerce')
            elif target_type == "string":
                df[column] = df[column].astype(str)
            elif target_type == "datetime":
                df[column] = pd.to_datetime(df[column], errors='coerce')
        
        elif transform_type == "normalize_text":
            # Text normalization
            if params.get("lowercase"):
                df[column] = df[column].str.lower()
            if params.get("strip"):
                df[column] = df[column].str.strip()
            if params.get("remove_special"):
                df[column] = df[column].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        
        elif transform_type == "remove_outliers":
            # Remove outliers using IQR method
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        
        elif transform_type == "fill_custom":
            # Fill missing values with custom value
            fill_value = params.get("value")
            df[column] = df[column].fillna(fill_value)
        
        elif transform_type == "create_bins":
            # Create bins for numeric column
            bins = params.get("bins", 5)
            df[f"{column}_binned"] = pd.cut(df[column], bins=bins)
        
        # Save transformed data
        transform_path = Path(session["parquet_path"]).parent / f"{session_id}_transformed.parquet"
        df.to_parquet(transform_path)
        
        csv_path = Path(session["parquet_path"]).parent / f"{session_id}_transformed.csv"
        df.to_csv(csv_path, index=False)
        
        return {
            "message": f"Transformation '{transform_type}' applied successfully",
            "rows": len(df),
            "columns": len(df.columns),
            "download_url": f"/api/download-transformed/{session_id}"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Error applying transformation: {str(e)}")

@router.get("/download-transformed/{session_id}")
async def download_transformed_data(session_id: str):
    """Download transformed dataset"""
    from fastapi.responses import FileResponse
    
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    csv_path = Path(session["parquet_path"]).parent / f"{session_id}_transformed.csv"
    if not csv_path.exists():
        raise HTTPException(404, "Transformed file not found")
    
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename=f"transformed_data_{session_id}.csv"
    )

@router.post("/pipeline/save/{session_id}")
async def save_pipeline(session_id: str, pipeline: Dict[str, Any] = Body(...)):
    """Save a cleaning pipeline for reuse"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        pipeline_name = pipeline.get("name", "Untitled Pipeline")
        steps = pipeline.get("steps", [])
        
        # Save pipeline to JSON file
        pipeline_dir = Path(session["parquet_path"]).parent / "pipelines"
        pipeline_dir.mkdir(exist_ok=True)
        
        pipeline_data = {
            "name": pipeline_name,
            "session_id": session_id,
            "steps": steps,
            "created_at": pd.Timestamp.now().isoformat()
        }
        
        pipeline_file = pipeline_dir / f"{session_id}_{pipeline_name.replace(' ', '_')}.json"
        with open(pipeline_file, 'w') as f:
            json.dump(pipeline_data, f, indent=2)
        
        return {
            "message": "Pipeline saved successfully",
            "pipeline_name": pipeline_name,
            "steps_count": len(steps)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Error saving pipeline: {str(e)}")

@router.get("/pipeline/list/{session_id}")
async def list_pipelines(session_id: str):
    """List saved pipelines for a session"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        pipeline_dir = Path(session["parquet_path"]).parent / "pipelines"
        
        if not pipeline_dir.exists():
            return {"pipelines": []}
        
        pipelines = []
        for pipeline_file in pipeline_dir.glob(f"{session_id}_*.json"):
            with open(pipeline_file, 'r') as f:
                pipeline_data = json.load(f)
                pipelines.append({
                    "name": pipeline_data.get("name"),
                    "steps_count": len(pipeline_data.get("steps", [])),
                    "created_at": pipeline_data.get("created_at"),
                    "filename": pipeline_file.name
                })
        
        return {"pipelines": pipelines}
    
    except Exception as e:
        raise HTTPException(500, f"Error listing pipelines: {str(e)}")

@router.post("/pipeline/apply/{session_id}")
async def apply_pipeline(session_id: str, pipeline_file: str = Body(..., embed=True)):
    """Apply a saved pipeline to current data"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        pipeline_dir = Path(session["parquet_path"]).parent / "pipelines"
        pipeline_path = pipeline_dir / pipeline_file
        
        if not pipeline_path.exists():
            raise HTTPException(404, "Pipeline not found")
        
        with open(pipeline_path, 'r') as f:
            pipeline_data = json.load(f)
        
        df = pd.read_parquet(session["parquet_path"])
        
        # Apply each step in the pipeline
        for step in pipeline_data.get("steps", []):
            step_type = step.get("type")
            
            if step_type == "fill_numeric_mean":
                for col in df.select_dtypes(include=['number']).columns:
                    df[col] = df[col].fillna(df[col].mean())
            
            elif step_type == "remove_duplicates":
                df = df.drop_duplicates()
            
            elif step_type == "drop_high_missing":
                threshold = step.get("threshold", 0.5)
                df = df.loc[:, df.isnull().mean() < threshold]
        
        # Save result
        result_path = Path(session["parquet_path"]).parent / f"{session_id}_pipeline_result.csv"
        df.to_csv(result_path, index=False)
        
        return {
            "message": "Pipeline applied successfully",
            "rows": len(df),
            "columns": len(df.columns),
            "download_url": f"/api/download-pipeline-result/{session_id}"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Error applying pipeline: {str(e)}")

@router.get("/download-pipeline-result/{session_id}")
async def download_pipeline_result(session_id: str):
    """Download pipeline result"""
    from fastapi.responses import FileResponse
    
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    result_path = Path(session["parquet_path"]).parent / f"{session_id}_pipeline_result.csv"
    if not result_path.exists():
        raise HTTPException(404, "Pipeline result not found")
    
    return FileResponse(
        path=result_path,
        media_type="text/csv",
        filename=f"pipeline_result_{session_id}.csv"
    )
