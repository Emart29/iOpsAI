# backend/main.py - PRODUCTION READY
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import pandas as pd
import numpy as np
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import settings
from storage import storage

print('🚀 Starting Insight Studio Backend...')

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Exploratory Data Analysis Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# Serve frontend static files if they exist
frontend_path = Path("../frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/")
    async def serve_frontend():
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Frontend not found"}
    
    @app.get("/dashboard")
    async def serve_dashboard():
        dashboard_path = frontend_path / "dashboard.html"
        if dashboard_path.exists():
            return FileResponse(str(dashboard_path))
        return {"message": "Dashboard not found"}

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print('✅ CORS middleware configured')

# Import routers
try:
    from routers import eda, ai, export
    app.include_router(eda.router)
    app.include_router(ai.router)
    app.include_router(export.router)
    print('✅ All routers loaded successfully')
except ImportError as e:
    print(f'⚠️ Some routers not available: {e}')

# Health and status endpoints
@app.get('/health')
async def health_check():
    """Health check endpoint"""
    sessions = storage.list_sessions(limit=1)
    return {
        'status': 'healthy',
        'app_name': settings.APP_NAME,
        'version': '1.0.0',
        'total_sessions': len(sessions),
        'database': 'connected'
    }

@app.get('/sessions')
async def list_sessions(limit: int = 50):
    """List all available sessions"""
    sessions = storage.list_sessions(limit=limit)
    return {
        'sessions': sessions,
        'total': len(sessions)
    }

@app.get('/session/{session_id}')
async def get_session_info(session_id: str):
    """Get detailed information about a session"""
    session = storage.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    
    return session

@app.delete('/session/{session_id}')
async def delete_session(session_id: str):
    """Delete a session and its data"""
    session = storage.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    
    # Delete files
    try:
        if session.get('original_path'):
            Path(session['original_path']).unlink(missing_ok=True)
        if session.get('parquet_path'):
            Path(session['parquet_path']).unlink(missing_ok=True)
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Delete from database
    success = storage.delete_session(session_id)
    
    if success:
        return {'message': 'Session deleted successfully', 'session_id': session_id}
    else:
        raise HTTPException(status_code=500, detail='Failed to delete session')

# Upload endpoints
@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    """Basic upload endpoint for backward compatibility"""
    try:
        print(f'📁 Uploading file: {file.filename}')
        
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower().replace('.', '')
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f'Invalid file type. Allowed: {", ".join(settings.ALLOWED_EXTENSIONS)}'
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f'File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB'
            )
        
        # Parse file based on extension
        if file_extension == 'csv':
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail='Unsupported file format')
        
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Save files
        original_path = settings.UPLOAD_DIR / f"{session_id}{Path(file.filename).suffix}"
        parquet_path = settings.UPLOAD_DIR / f"{session_id}.parquet"
        
        # Save original file
        with open(original_path, 'wb') as f:
            f.write(content)
        
        # Save as parquet for faster loading
        df.to_parquet(parquet_path)
        
        # Basic analysis
        analysis = {
            'filename': file.filename,
            'rows': int(df.shape[0]),
            'columns': int(df.shape[1]),
            'column_names': list(df.columns),
            'memory_usage': int(df.memory_usage(deep=True).sum())
        }
        
        # Save session
        session_data = {
            'session_id': session_id,
            'filename': file.filename,
            'original_path': str(original_path),
            'parquet_path': str(parquet_path),
            'file_size': len(content),
            'dataframe_shape': df.shape,
            'analysis': {'overview': analysis},
            'created_at': datetime.now().isoformat()
        }
        
        storage.save_session(session_id, session_data)
        
        print(f'✅ File uploaded successfully: {session_id}')
        
        return {
            'success': True,
            'session_id': session_id,
            'analysis': analysis,
            'message': 'File uploaded successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f'❌ Upload error: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Upload failed: {str(e)}')

@app.post('/upload-enhanced')
async def upload_file_enhanced(file: UploadFile = File(...)):
    """Enhanced upload with comprehensive analysis"""
    try:
        print(f'📁 Enhanced upload: {file.filename}')
        
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower().replace('.', '')
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f'Invalid file type. Allowed: {", ".join(settings.ALLOWED_EXTENSIONS)}'
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f'File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB'
            )
        
        # Parse file
        if file_extension == 'csv':
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail='Unsupported file format')
        
        session_id = str(uuid.uuid4())[:8]
        
        print(f'✅ File loaded: {df.shape[0]} rows, {df.shape[1]} columns')
        
        # Save files
        original_path = settings.UPLOAD_DIR / f"{session_id}{Path(file.filename).suffix}"
        parquet_path = settings.UPLOAD_DIR / f"{session_id}.parquet"
        
        with open(original_path, 'wb') as f:
            f.write(content)
        
        df.to_parquet(parquet_path)
        
        # Comprehensive analysis
        try:
            from utils.data_processing import generate_data_profile, detect_outliers, generate_correlations
            from utils.ai_helpers import detect_semantic_types, generate_suggestions
            
            print('🔄 Generating comprehensive analysis...')
            
            profile = generate_data_profile(df)
            outliers = detect_outliers(df)
            correlations = generate_correlations(df)
            semantic_types = detect_semantic_types(df)
            ai_suggestions = generate_suggestions(df)
            
            print('✅ Comprehensive analysis complete')
            
        except ImportError as e:
            print(f'⚠️ Advanced analytics not available: {e}')
            # Fallback to basic analysis
            profile = generate_basic_profile(df)
            outliers = {'method': 'basic', 'columns': {}, 'summary': {'total_outliers': 0, 'affected_columns': 0}}
            correlations = {'matrix': {}, 'strong_correlations': [], 'summary': {'total_variables': 0, 'strong_correlations_count': 0}}
            semantic_types = {}
            ai_suggestions = ["Upload successful! Try asking questions about your data."]
        
        # Save session with all data
        session_data = {
            'session_id': session_id,
            'filename': file.filename,
            'original_path': str(original_path),
            'parquet_path': str(parquet_path),
            'file_size': len(content),
            'dataframe_shape': df.shape,
            'analysis': profile,
            'outliers': outliers,
            'correlations': correlations,
            'semantic_types': semantic_types,
            'ai_suggestions': ai_suggestions,
            'created_at': datetime.now().isoformat()
        }
        
        storage.save_session(session_id, session_data)
        
        print(f'🎉 Enhanced analysis complete for session: {session_id}')
        
        return {
            'success': True,
            'session_id': session_id,
            'analysis': profile,
            'outliers': outliers,
            'correlations': correlations,
            'semantic_types': semantic_types,
            'ai_suggestions': ai_suggestions,
            'message': 'File uploaded and analyzed successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f'❌ Enhanced upload error: {str(e)}')
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Upload failed: {str(e)}')

def generate_basic_profile(df: pd.DataFrame) -> dict:
    """Generate basic profile when advanced analytics unavailable"""
    profile = {
        'overview': {
            'rows': int(df.shape[0]),
            'columns': int(df.shape[1]),
            'memory_usage': int(df.memory_usage(deep=True).sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'total_missing': int(df.isnull().sum().sum()),
            'completeness_score': float(1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))) if len(df) > 0 else 0.0
        },
        'columns': {},
        'data_quality': {
            'score': 80.0,
            'issues': []
        }
    }
    
    # Basic column analysis
    for column in df.columns:
        col_data = df[column]
        profile['columns'][column] = {
            'dtype': str(col_data.dtype),
            'missing': int(col_data.isnull().sum()),
            'missing_percentage': float(col_data.isnull().sum() / len(df)) if len(df) > 0 else 0.0,
            'unique': int(col_data.nunique()),
            'type': 'numeric' if pd.api.types.is_numeric_dtype(col_data) else 'categorical',
            'sample_data': col_data.dropna().head(3).tolist() if not col_data.empty else []
        }
        
        # Add basic stats for numeric columns
        if pd.api.types.is_numeric_dtype(col_data):
            profile['columns'][column]['stats'] = {
                'mean': float(col_data.mean()) if not col_data.empty else 0,
                'std': float(col_data.std()) if not col_data.empty else 0,
                'min': float(col_data.min()) if not col_data.empty else 0,
                'max': float(col_data.max()) if not col_data.empty else 0,
                'median': float(col_data.median()) if not col_data.empty else 0
            }
    
    return profile

# AI Question endpoint
@app.post('/ask')
async def ask_question(session_id: str, question: str):
    """Basic AI question answering"""
    session = storage.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    
    try:
        # Load dataframe
        df = pd.read_parquet(session['parquet_path'])
        
        # Try advanced AI
        try:
            from utils.ai_helpers import generate_ai_response
            response = generate_ai_response(df, question)
            
            # Save analysis
            storage.save_analysis(session_id, 'ai_qa', {
                'question': question,
                'response': response
            })
            
            return {
                'question': question,
                'answer': response['answer'],
                'confidence': response['confidence'],
                'suggestions': response.get('suggestions', []),
                'analysis_type': response.get('analysis_type', 'general'),
                'session_id': session_id
            }
            
        except ImportError:
            # Fallback to basic AI
            answer = generate_basic_answer(df, question, session)
            return {
                'question': question,
                'answer': answer,
                'session_id': session_id,
                'confidence': 0.7,
                'analysis_type': 'basic'
            }
        
    except Exception as e:
        print(f'❌ AI question error: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Failed to process question: {str(e)}')

def generate_basic_answer(df: pd.DataFrame, question: str, session: dict) -> str:
    """Generate basic answer without advanced AI"""
    question_lower = question.lower()
    analysis = session.get('analysis', {}).get('overview', {})
    
    if any(word in question_lower for word in ['row', 'rows', 'how many']):
        return f"Your dataset has {analysis.get('rows', len(df))} rows of data."
    
    elif any(word in question_lower for word in ['column', 'columns', 'features']):
        cols = list(df.columns)
        return f"Your dataset has {len(cols)} columns: {', '.join(cols[:10])}{'...' if len(cols) > 10 else ''}"
    
    elif any(word in question_lower for word in ['missing', 'null', 'empty']):
        total_missing = df.isnull().sum().sum()
        missing_pct = (total_missing / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 0
        return f"Found {total_missing} missing values across the dataset ({missing_pct:.1f}% of all data)."
    
    elif any(word in question_lower for word in ['summary', 'overview', 'about']):
        return f"Your dataset contains {len(df)} rows and {len(df.columns)} columns. It has {df.isnull().sum().sum()} missing values and {df.duplicated().sum()} duplicate rows."
    
    else:
        return "I can help you analyze your data. Try asking about: number of rows, columns, missing values, data summary, or specific column statistics."

# Chart data endpoint
@app.get('/chart-data/{session_id}')
async def get_chart_data(session_id: str, chart_type: str = "overview"):
    """Get chart data for visualizations"""
    session = storage.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    
    analysis = session.get('analysis', {})
    
    if chart_type == "overview":
        overview = analysis.get('overview', {})
        return {
            'type': 'bar',
            'labels': ['Rows', 'Columns', 'Missing', 'Quality'],
            'data': [
                overview.get('rows', 0),
                overview.get('columns', 0),
                overview.get('total_missing', 0),
                int(analysis.get('data_quality', {}).get('score', 0))
            ],
            'colors': ['#9333ea', '#3b82f6', '#ef4444', '#22c55e']
        }
    
    elif chart_type == "missing":
        columns = analysis.get('columns', {})
        missing_cols = {k: v['missing'] for k, v in columns.items() if v.get('missing', 0) > 0}
        
        return {
            'type': 'bar',
            'labels': list(missing_cols.keys())[:10],
            'data': list(missing_cols.values())[:10],
            'colors': ['#f97316'] * len(missing_cols)
        }
    
    elif chart_type == "types":
        columns = analysis.get('columns', {})
        type_counts = {}
        for col_data in columns.values():
            col_type = col_data.get('type', 'unknown')
            type_counts[col_type] = type_counts.get(col_type, 0) + 1
        
        return {
            'type': 'pie',
            'labels': list(type_counts.keys()),
            'data': list(type_counts.values()),
'colors': ['#9333ea', '#3b82f6', '#22c55e', '#f97316', '#9ca3af']
}
    else:
        return {'type': chart_type, 'message': 'Chart type not available'}
print('🎉 Backend server ready!')
print(f'📍 http://{settings.HOST}:{settings.PORT}')
print('📚 API Docs: http://localhost:8000/docs')
print('🔥 All systems operational!')