"""
API Router for AI-powered insights and chat
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict, Any, List
from storage import storage
from database import get_db
from models import Experiment
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

router = APIRouter(prefix="/api", tags=["ai"])

@router.post("/insights/{session_id}")
async def generate_insights(session_id: str, db: Session = Depends(get_db)):
    """Generate AI-powered insights for the dataset"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        from utils.ai_helpers import generate_ai_insights
        
        insights = generate_ai_insights(df)
        
        # Log to database
        # Note: Experiment model has fields: session_id, dataset_name, insights_generated, status
        exp = Experiment(
            session_id=session_id,
            dataset_name=session.get("filename", "unknown"),
            insights_generated=True,
            status="completed"
        )
        db.add(exp)
        db.commit()
        
        return insights
    except Exception as e:
        raise HTTPException(500, f"Error generating insights: {str(e)}")

@router.post("/chat")
async def chat_with_sight(body: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Chat with Sight AI about the dataset"""
    session_id = body.get("session_id")
    message = body.get("message", "").strip()
    chat_history = body.get("chat_history", [])
    
    if not session_id or not message:
        raise HTTPException(400, "session_id and message are required")
    
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        from utils.ai_helpers import chat_with_data
        
        response = chat_with_data(df, message, chat_history, session.get("filename", "dataset"))
        
        # Log experiment
        # We don't have a specific 'chat' field in Experiment, so we just log it as an activity
        # or we could skip logging for chat if not needed for the history view
        exp = Experiment(
            session_id=session_id,
            dataset_name=session.get("filename", "unknown"),
            status="chat_interaction"
        )
        db.add(exp)
        db.commit()
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(500, f"Chat error: {str(e)}")

@router.post("/recommendations/{session_id}")
async def get_recommendations(session_id: str):
    """Get AI recommendations for modeling and next steps"""
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    try:
        df = pd.read_parquet(session["parquet_path"])
        from utils.ai_helpers import generate_recommendations
        
        recommendations = generate_recommendations(df)
        return recommendations
    except Exception as e:
        raise HTTPException(500, f"Error generating recommendations: {str(e)}")