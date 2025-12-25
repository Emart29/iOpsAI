# backend/utils/usage_tracking.py
"""
Usage tracking utilities for tier management and limit enforcement.
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from models import UsageTracking, User
from config import settings


def get_current_month_year() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.utcnow().strftime("%Y-%m")


def get_or_create_usage(db: Session, user_id: str, month_year: Optional[str] = None) -> UsageTracking:
    """
    Get or create usage tracking record for a user and month.
    
    Args:
        db: Database session
        user_id: User ID (UUID string or integer)
        month_year: Month in YYYY-MM format (defaults to current month)
    
    Returns:
        UsageTracking: Usage tracking record
    """
    if month_year is None:
        month_year = get_current_month_year()
    
    # Convert user_id to string if it's an integer (for backward compatibility)
    user_id_str = str(user_id)
    
    # Try to get existing record
    usage = db.query(UsageTracking).filter(
        UsageTracking.user_id == user_id_str,
        UsageTracking.month_year == month_year
    ).first()
    
    # Create new record if it doesn't exist
    if not usage:
        usage = UsageTracking(
            user_id=user_id_str,
            month_year=month_year,
            datasets_count=0,
            ai_messages_count=0,
            reports_count=0
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
    
    return usage


def reset_monthly_usage(db: Session) -> int:
    """
    Reset usage counters for all users at the start of a new month.
    This should be called by a cron job on the 1st of each month.
    
    Args:
        db: Database session
    
    Returns:
        int: Number of users whose usage was reset
    """
    current_month = get_current_month_year()
    
    # Get all users
    users = db.query(User).all()
    reset_count = 0
    
    for user in users:
        # Get or create usage record for current month
        # This will create a fresh record with zero counts
        usage = get_or_create_usage(db, user.id, current_month)
        
        # If the record already existed with non-zero counts, reset them
        if usage.datasets_count > 0 or usage.ai_messages_count > 0 or usage.reports_count > 0:
            usage.datasets_count = 0
            usage.ai_messages_count = 0
            usage.reports_count = 0
            usage.updated_at = datetime.utcnow()
            reset_count += 1
    
    db.commit()
    return reset_count


def check_usage_limit(db: Session, user_id: str, resource_type: str) -> tuple[bool, Optional[str]]:
    """
    Check if user has reached their usage limit for a resource type.
    
    Args:
        db: Database session
        user_id: User ID
        resource_type: Type of resource ('dataset', 'ai_message', 'report')
    
    Returns:
        tuple: (can_proceed: bool, error_message: Optional[str])
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, "User not found"
    
    # Get tier limits
    tier_name = user.tier.value if hasattr(user.tier, 'value') else user.tier
    limits = settings.TIER_LIMITS.get(tier_name, settings.TIER_LIMITS["free"])
    
    # Get current usage
    usage = get_or_create_usage(db, user_id)
    
    # Check limit based on resource type
    if resource_type == "dataset":
        limit = limits["datasets_per_month"]
        current = usage.datasets_count
        resource_name = "dataset"
    elif resource_type == "ai_message":
        limit = limits["ai_messages_per_month"]
        current = usage.ai_messages_count
        resource_name = "AI message"
    elif resource_type == "report":
        limit = limits["reports_per_month"]
        current = usage.reports_count
        resource_name = "public report"
    else:
        return False, f"Unknown resource type: {resource_type}"
    
    # -1 means unlimited
    if limit == -1:
        return True, None
    
    # Check if limit is reached
    if current >= limit:
        return False, f"You've reached your monthly {resource_name} limit ({current}/{limit}). Please upgrade your plan."
    
    return True, None


def increment_usage(db: Session, user_id: str, resource_type: str) -> bool:
    """
    Increment usage counter for a resource type.
    
    Args:
        db: Database session
        user_id: User ID
        resource_type: Type of resource ('dataset', 'ai_message', 'report')
    
    Returns:
        bool: True if incremented successfully, False otherwise
    """
    usage = get_or_create_usage(db, user_id)
    
    if resource_type == "dataset":
        usage.datasets_count += 1
    elif resource_type == "ai_message":
        usage.ai_messages_count += 1
    elif resource_type == "report":
        usage.reports_count += 1
    else:
        return False
    
    usage.updated_at = datetime.utcnow()
    db.commit()
    return True


def get_usage_stats(db: Session, user_id: str) -> dict:
    """
    Get current usage statistics for a user.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        dict: Usage statistics with limits
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}
    
    # Get tier limits
    tier_name = user.tier.value if hasattr(user.tier, 'value') else user.tier
    limits = settings.TIER_LIMITS.get(tier_name, settings.TIER_LIMITS["free"])
    
    # Get current usage
    usage = get_or_create_usage(db, user_id)
    
    return {
        "tier": tier_name,
        "month_year": usage.month_year,
        "datasets": {
            "current": usage.datasets_count,
            "limit": limits["datasets_per_month"],
            "unlimited": limits["datasets_per_month"] == -1
        },
        "ai_messages": {
            "current": usage.ai_messages_count,
            "limit": limits["ai_messages_per_month"],
            "unlimited": limits["ai_messages_per_month"] == -1
        },
        "reports": {
            "current": usage.reports_count,
            "limit": limits["reports_per_month"],
            "unlimited": limits["reports_per_month"] == -1
        }
    }
