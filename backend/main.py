# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any
from config import settings
from storage import storage
from database import init_db
from models import Experiment
from database import get_db
from sqlalchemy.orm import Session
from utils.upload_handler import process_upload_file
from utils.data_processing import generate_plotly_data

# Initialize Sentry for error tracking (before app creation)
from utils.sentry_integration import init_sentry, capture_exception
sentry_initialized = init_sentry()

print('Starting iOps Backend...')

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Data Science Copilot",
    version="2.0.0",
)

# Initialize DB
init_db()

# CORS - Configure for production
# In production, use specific origins from CORS_ORIGINS environment variable
# In development, allow all origins for convenience
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
try:
    from routers import auth, datasets, ai, eda, export, data_grid, automl, health
    app.include_router(health.router)  # Health check routes (for UptimeRobot)
    app.include_router(auth.router)  # Authentication routes (Phase 1)
    app.include_router(datasets.router)
    app.include_router(ai.router)
    app.include_router(eda.router)
    app.include_router(export.router)
    app.include_router(data_grid.router)
    app.include_router(automl.router)
except ImportError as e:
    print(f"Some routers unavailable: {e}")

# Note: Health check endpoints are now in routers/health.py
# The /health endpoint is handled by the health router for UptimeRobot monitoring

@app.get("/api/experiments")
async def get_experiments(db: Session = Depends(get_db)):
    """Get experiment log"""
    experiments = db.query(Experiment).order_by(Experiment.timestamp.desc()).limit(50).all()
    return [
        {
            "id": exp.id,
            "session_id": exp.session_id,
            "dataset_name": exp.dataset_name,
            "timestamp": exp.timestamp.isoformat(),
            "rows": exp.rows or 0,
            "columns": exp.columns or 0,
            "insights_generated": exp.insights_generated,
            "report_generated": exp.report_generated,
            "status": exp.status
        }
        for exp in experiments
    ]

@app.delete("/api/experiments/{session_id}")
async def delete_experiment(session_id: str):
    """Delete an experiment"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    # Delete files
    for key in ("original_path", "parquet_path"):
        path = session.get(key)
        if path:
            Path(path).unlink(missing_ok=True)
    
    storage.delete_session(session_id)
    return {"message": "Deleted", "session_id": session_id}

@app.get("/api/charts/{session_id}")
async def get_charts(session_id: str):
    """Get interactive Plotly chart data"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        charts = generate_plotly_data(df)
        return charts
    except Exception as e:
        raise HTTPException(500, f"Error generating charts: {str(e)}")

@app.post("/api/generate-report/{session_id}")
async def generate_report(session_id: str):
    """Generate EDA PDF report"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    # For MVP, return a placeholder
    return {
        "download_url": f"/api/download-report/{session_id}",
        "message": "Report generation in progress"
    }

@app.get("/api/download-report/{session_id}")
async def download_report(session_id: str):
    """Download the generated report"""
    return Response(
        content=f"Report for session {session_id}\\n\\nAnalysis not yet implemented.",
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=report_{session_id}.txt"}
    )

@app.post("/api/clean-data/{session_id}")
async def clean_data(session_id: str, body: Dict[str, Any] = Body(...)):
    """Clean dataset based on selected operations"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    cleaning_steps = body.get("cleaning_steps", [])
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        df_clean = df.copy()
        
        # Apply cleaning operations
        if "fill_numeric_mean" in cleaning_steps:
            for col in df_clean.select_dtypes(include=[np.number]).columns:
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        
        if "remove_duplicates" in cleaning_steps:
            df_clean = df_clean.drop_duplicates()
        
        if "drop_high_missing" in cleaning_steps:
            threshold = 0.5
            df_clean = df_clean.loc[:, df_clean.isnull().mean() < threshold]
        
        # Save cleaned data
        clean_path = Path(session["parquet_path"]).parent / f"{session_id}_cleaned.csv"
        df_clean.to_csv(clean_path, index=False)
        
        return {
            "download_url": f"/api/download-clean/{session_id}",
            "summary": f"Applied {len(cleaning_steps)} cleaning operations. Rows: {len(df_clean)}, Columns: {len(df_clean.columns)}"
        }
    except Exception as e:
        raise HTTPException(500, f"Error cleaning data: {str(e)}")

@app.get("/api/download-clean/{session_id}")
async def download_clean_data(session_id: str):
    """Download the cleaned dataset"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    clean_path = Path(session["parquet_path"]).parent / f"{session_id}_cleaned.csv"
    if not clean_path.exists():
        raise HTTPException(404, "Cleaned file not found")
        
    return FileResponse(
        path=clean_path,
        media_type="text/csv",
        filename=f"cleaned_data_{session_id}.csv"
    )

@app.get("/api/generate-script/{session_id}")
async def generate_script(session_id: str):
    """Generate Python script for analysis"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    filename = session.get("filename", "data.csv")
    
    script = f'''"""
Auto-generated by iOps: Data Science Copilot
Dataset: {filename}
Generated: {datetime.now().isoformat()}
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('{filename}')
print(f"Dataset shape: {{df.shape}}")

# Data overview
print(df.info())
print(df.describe())

# Handle missing values
print("\\nMissing values:")
print(df.isnull().sum())

# Visualizations
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
for col in numeric_cols:
    plt.figure(figsize=(10, 6))
    sns.histplot(df[col])
    plt.title(f'Distribution of {{col}}')
    plt.show()

# Save cleaned data
df.to_csv('{filename.replace(".csv", "_cleaned.csv")}', index=False)
print("Analysis complete!")
'''
    
    return {"script": script}

print("iOps Backend READY! http://localhost:8000")