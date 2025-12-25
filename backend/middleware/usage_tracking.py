# backend/middleware/usage_tracking.py
"""
Usage tracking middleware for enforcing tier limits.
Tracks and enforces limits on datasets, AI messages, and reports.
"""
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User
from utils.usage_tracking import check_usage_limit, increment_usage
from utils.auth import get_current_user


def _track_usage_internal(
    resource_type: str,
    current_user: User,
    db: Session
) -> User:
    """
    Internal function to track resource usage and enforce tier limits.
    
    Args:
        resource_type: Type of resource being consumed ('dataset', 'ai_message', 'report')
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User: The current user if limits are not exceeded
    
    Raises:
        HTTPException: 403 if usage limit is exceeded
    """
    # Check if user has reached their limit
    can_proceed, error_message = check_usage_limit(db, current_user.id, resource_type)
    
    if not can_proceed:
        # Get tier name for upgrade URL
        tier_name = current_user.tier.value if hasattr(current_user.tier, 'value') else current_user.tier
        
        # Return 403 with upgrade prompt
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "USAGE_LIMIT_EXCEEDED",
                    "message": error_message,
                    "details": {
                        "resource_type": resource_type,
                        "tier": tier_name,
                        "upgrade_url": "/pricing"
                    }
                }
            }
        )
    
    # Increment usage counter
    success = increment_usage(db, current_user.id, resource_type)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track usage for resource type: {resource_type}"
        )
    
    return current_user


def track_dataset_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency for tracking dataset uploads.
    
    Usage:
        @app.post("/api/datasets")
        async def upload_dataset(
            user: User = Depends(track_dataset_usage)
        ):
            # Your endpoint logic here
            pass
    """
    return _track_usage_internal("dataset", current_user, db)


def track_ai_message_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency for tracking AI message usage.
    
    Usage:
        @app.post("/api/ai/chat")
        async def send_ai_message(
            user: User = Depends(track_ai_message_usage)
        ):
            # Your endpoint logic here
            pass
    """
    return _track_usage_internal("ai_message", current_user, db)


def track_report_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency for tracking public report creation.
    
    Usage:
        @app.post("/api/reports")
        async def create_report(
            user: User = Depends(track_report_usage)
        ):
            # Your endpoint logic here
            pass
    """
    return _track_usage_internal("report", current_user, db)
