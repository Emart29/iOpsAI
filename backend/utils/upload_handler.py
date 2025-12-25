import io
import uuid
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException
from config import settings
from storage import storage
from utils.data_processing import generate_basic_profile, generate_data_profile, detect_outliers, generate_correlations

# Safe import for AI features
try:
    from utils.ai_helpers import detect_semantic_types, generate_suggestions
except ImportError:
    detect_semantic_types = None
    generate_suggestions = None

async def process_upload_file(file: UploadFile, enhanced: bool):
    ext = Path(file.filename).suffix.lower().lstrip('.')
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Invalid file type: {ext}")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    # Load data
    try:
        if ext == 'csv':
            df = pd.read_csv(io.StringIO(content.decode('utf-8', errors='replace')))
        elif ext == 'json':
            df = pd.read_json(io.BytesIO(content))
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(400, "Unsupported file format")
    except Exception as e:
        raise HTTPException(400, f"Error reading file: {str(e)}")

    session_id = str(uuid.uuid4())[:8]
    orig_path = settings.UPLOAD_DIR / f"{session_id}_{file.filename}"
    parquet_path = settings.UPLOAD_DIR / f"{session_id}.parquet"
    
    # Ensure upload directory exists
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    orig_path.write_bytes(content)
    df.to_parquet(parquet_path, compression="gzip")

    profile = generate_basic_profile(df)
    outliers = correlations = semantic = suggestions = {}

    if enhanced:
        try:
            # Generate comprehensive analysis
            profile = generate_data_profile(df)
            outliers = detect_outliers(df)
            correlations = generate_correlations(df)
            
            if detect_semantic_types and generate_suggestions:
                semantic_types = detect_semantic_types(df)
                ai_suggestions = generate_suggestions(df, semantic_types)
                semantic = semantic_types
                suggestions = ai_suggestions
        except Exception as e:
            print(f"Enhanced analysis skipped (normal): {e}")

    session_data = {
        "session_id": session_id,
        "filename": file.filename,
        "original_path": str(orig_path),
        "parquet_path": str(parquet_path),
        "analysis": profile,
        "outliers": outliers,
        "correlations": correlations,
        "semantic_types": semantic,
        "ai_suggestions": suggestions or ["Ready to chat!"],
        "created_at": datetime.now().isoformat(),
        "analyses": []
    }
    storage.save_session(session_id, session_data)

    return {
        "success": True,
        "session_id": session_id,
        "analysis": profile,
        "outliers": outliers,
        "correlations": correlations,
        "semantic_types": semantic,
        "ai_suggestions": suggestions or [],
    }
