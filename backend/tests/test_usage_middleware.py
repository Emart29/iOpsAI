# backend/tests/test_usage_middleware.py
"""
Tests for usage tracking middleware.
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from models import Base, User, UsageTracking, UserTier
from middleware.usage_tracking import _track_usage_internal
from utils.usage_tracking import get_or_create_usage


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test free tier user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        tier=UserTier.FREE,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_pro_user(db):
    """Create a test pro user."""
    user = User(
        email="pro@example.com",
        username="prouser",
        hashed_password="hashed_password",
        tier=UserTier.PRO,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_track_dataset_usage_success(db, test_user):
    """Test successful dataset usage tracking."""
    # Should succeed and increment counter
    result = _track_usage_internal("dataset", test_user, db)
    
    assert result == test_user
    
    # Verify usage was incremented
    usage = get_or_create_usage(db, test_user.id)
    assert usage.datasets_count == 1


def test_track_dataset_usage_at_limit(db, test_user):
    """Test dataset usage tracking when at limit."""
    # Set usage to limit (5 for free tier)
    usage = get_or_create_usage(db, test_user.id)
    usage.datasets_count = 5
    db.commit()
    
    # Should raise HTTPException with 403
    with pytest.raises(HTTPException) as exc_info:
        _track_usage_internal("dataset", test_user, db)
    
    assert exc_info.value.status_code == 403
    assert "USAGE_LIMIT_EXCEEDED" in str(exc_info.value.detail)
    
    # Verify usage was NOT incremented
    db.refresh(usage)
    assert usage.datasets_count == 5


def test_track_ai_message_usage_success(db, test_user):
    """Test successful AI message usage tracking."""
    result = _track_usage_internal("ai_message", test_user, db)
    
    assert result == test_user
    
    # Verify usage was incremented
    usage = get_or_create_usage(db, test_user.id)
    assert usage.ai_messages_count == 1


def test_track_ai_message_usage_at_limit(db, test_user):
    """Test AI message usage tracking when at limit."""
    # Set usage to limit (50 for free tier)
    usage = get_or_create_usage(db, test_user.id)
    usage.ai_messages_count = 50
    db.commit()
    
    # Should raise HTTPException with 403
    with pytest.raises(HTTPException) as exc_info:
        _track_usage_internal("ai_message", test_user, db)
    
    assert exc_info.value.status_code == 403
    
    # Verify usage was NOT incremented
    db.refresh(usage)
    assert usage.ai_messages_count == 50


def test_track_report_usage_success(db, test_user):
    """Test successful report usage tracking."""
    result = _track_usage_internal("report", test_user, db)
    
    assert result == test_user
    
    # Verify usage was incremented
    usage = get_or_create_usage(db, test_user.id)
    assert usage.reports_count == 1


def test_track_report_usage_at_limit(db, test_user):
    """Test report usage tracking when at limit."""
    # Set usage to limit (3 for free tier)
    usage = get_or_create_usage(db, test_user.id)
    usage.reports_count = 3
    db.commit()
    
    # Should raise HTTPException with 403
    with pytest.raises(HTTPException) as exc_info:
        _track_usage_internal("report", test_user, db)
    
    assert exc_info.value.status_code == 403
    
    # Verify usage was NOT incremented
    db.refresh(usage)
    assert usage.reports_count == 3


def test_track_usage_pro_tier_unlimited(db, test_pro_user):
    """Test that pro tier users have unlimited usage."""
    # Set high usage counts
    usage = get_or_create_usage(db, test_pro_user.id)
    usage.datasets_count = 100
    usage.ai_messages_count = 500
    usage.reports_count = 50
    db.commit()
    
    # Should still succeed for all resource types
    result = _track_usage_internal("dataset", test_pro_user, db)
    assert result == test_pro_user
    
    result = _track_usage_internal("ai_message", test_pro_user, db)
    assert result == test_pro_user
    
    result = _track_usage_internal("report", test_pro_user, db)
    assert result == test_pro_user
    
    # Verify usage was incremented
    db.refresh(usage)
    assert usage.datasets_count == 101
    assert usage.ai_messages_count == 501
    assert usage.reports_count == 51


def test_track_usage_error_message_format(db, test_user):
    """Test that error message includes upgrade prompt."""
    # Set usage to limit
    usage = get_or_create_usage(db, test_user.id)
    usage.datasets_count = 5
    db.commit()
    
    # Should raise HTTPException with proper error format
    with pytest.raises(HTTPException) as exc_info:
        _track_usage_internal("dataset", test_user, db)
    
    error_detail = exc_info.value.detail
    assert "error" in error_detail
    assert error_detail["error"]["code"] == "USAGE_LIMIT_EXCEEDED"
    assert "message" in error_detail["error"]
    assert "details" in error_detail["error"]
    assert error_detail["error"]["details"]["tier"] == "free"
    assert error_detail["error"]["details"]["upgrade_url"] == "/pricing"
    assert error_detail["error"]["details"]["resource_type"] == "dataset"


def test_track_usage_multiple_increments(db, test_user):
    """Test multiple usage increments."""
    # Track 3 datasets
    for i in range(3):
        _track_usage_internal("dataset", test_user, db)
    
    # Verify count
    usage = get_or_create_usage(db, test_user.id)
    assert usage.datasets_count == 3
    
    # Track 2 more (should succeed, total 5)
    for i in range(2):
        _track_usage_internal("dataset", test_user, db)
    
    db.refresh(usage)
    assert usage.datasets_count == 5
    
    # 6th should fail
    with pytest.raises(HTTPException):
        _track_usage_internal("dataset", test_user, db)


def test_track_usage_different_resource_types(db, test_user):
    """Test tracking different resource types independently."""
    # Track datasets
    _track_usage_internal("dataset", test_user, db)
    _track_usage_internal("dataset", test_user, db)
    
    # Track AI messages
    _track_usage_internal("ai_message", test_user, db)
    
    # Track reports
    _track_usage_internal("report", test_user, db)
    
    # Verify all counters are independent
    usage = get_or_create_usage(db, test_user.id)
    assert usage.datasets_count == 2
    assert usage.ai_messages_count == 1
    assert usage.reports_count == 1


def test_track_usage_creates_usage_record_if_not_exists(db, test_user):
    """Test that tracking creates usage record if it doesn't exist."""
    # Verify no usage record exists
    usage = db.query(UsageTracking).filter(
        UsageTracking.user_id == str(test_user.id)
    ).first()
    assert usage is None
    
    # Track usage
    _track_usage_internal("dataset", test_user, db)
    
    # Verify record was created
    usage = db.query(UsageTracking).filter(
        UsageTracking.user_id == str(test_user.id)
    ).first()
    assert usage is not None
    assert usage.datasets_count == 1
