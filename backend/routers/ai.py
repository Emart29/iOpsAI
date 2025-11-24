from storage import storage
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
import numpy as np
from typing import Dict, Any, List

from deps import get_sessions
from utils.ai_helpers import generate_ai_response, detect_semantic_types, generate_suggestions

router = APIRouter(prefix="/ai", tags=["artificial intelligence"])

@router.post("/qa")
async def ai_question_answer(
    session_id: str,
    question: str,
    sessions: dict = Depends(get_sessions)
):
    """AI-powered question answering about the dataset"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        file_path = sessions[session_id]['file_path']
        df = pd.read_parquet(file_path)
        response = generate_ai_response(df, question)
        
        sessions[session_id]['analyses'].append({
            'type': 'ai_qa',
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response
        })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing AI question: {str(e)}")

@router.post("/suggest")
async def get_ai_suggestions(
    session_id: str, 
    goal: str = None,
    sessions: dict = Depends(get_sessions)
):
    """Get AI suggestions for data analysis"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = sessions[session_id]['file_path']
    
    try:
        df = pd.read_parquet(file_path)
        suggestions = generate_suggestions(df, goal)
        
        return {
            "goal": goal,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@router.post("/detect-types")
async def detect_column_types(
    session_id: str,
    sessions: dict = Depends(get_sessions)
):
    """Smart semantic detection of column types"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = sessions[session_id]['file_path']
    
    try:
        df = pd.read_parquet(file_path)
        type_detection = detect_semantic_types(df)
        
        sessions[session_id]['analyses'].append({
            'type': 'semantic_type_detection',
            'timestamp': datetime.now().isoformat(),
            'results': type_detection
        })
        
        return type_detection
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting column types: {str(e)}")