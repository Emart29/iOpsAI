# backend/tests/test_usage_tracking.py
"""
Tests for usage tracking functionality.
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import Base, User, UsageTracking, UserTier
from utils.usage_tracking import (
    get_or_create_usage,
    reset_monthly_usage,
    check_usage_limit,
    increment_usage,
    get_usage_stats,
    get_current_month_year
)


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
    """Create a test user."""
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


def test_get_current_month_year():
    """Test getting current month in YYYY-MM format."""
    month_year = get_current_month_year()
    assert len(month_year) == 7
    assert month_year[4] == "-"
    # Verify it's a valid date format
    datetime.strptime(month_year, "%Y-%m")


def test_get_or_create_usage_creates_new(db, test_user):
    """Test that get_or_create_usage creates a new record if it doesn't exist."""
    month_year = "2024-12"
    
    # Verify no usage record exists
    existing = db.query(UsageTracking).filter(
        UsageTracking.user_id == str(test_user.id),
        UsageTracking.month_year == month_year
    ).first()
    assert existing is None
    
    # Get or create usage
    usage = get_or_create_usage(db, test_user.id, month_year)
    
    # Verify record was created
    assert usage is not None
    assert usage.user_id == str(test_user.id)
    assert usage.month_year == month_year
    assert usage.datasets_count == 0
    assert usage.ai_messages_count == 0
    assert usage.reports_count == 0


def test_get_or_create_usage_returns_existing(db, test_user):
    """Test that get_or_create_usage returns existing record."""
    month_year = "2024-12"
    
    # Create initial usage record
    usage1 = get_or_create_usage(db, test_user.id, month_year)
    usage1.datasets_count = 3
    db.commit()
    
    # Get the same record again
    usage2 = get_or_create_usage(db, test_user.id, month_year)
    
    # Verify it's the same record
    assert usage1.id == usage2.id
    assert usage2.datasets_count == 3


def test_get_or_create_usage_defaults_to_current_month(db, test_user):
    """Test that get_or_create_usage defaults to current month."""
    usage = get_or_create_usage(db, test_user.id)
    
    current_month = get_current_month_year()
    assert usage.month_year == current_month


def test_unique_constraint_on_user_month(db, test_user):
    """Test that unique constraint prevents duplicate user/month records."""
    month_year = "2024-12"
    
    # Create first record
    usage1 = UsageTracking(
        user_id=str(test_user.id),
        month_year=month_year,
        datasets_count=0,
        ai_messages_count=0,
        reports_count=0
    )
    db.add(usage1)
    db.commit()
    
    # Try to create duplicate record
    usage2 = UsageTracking(
        user_id=str(test_user.id),
        month_year=month_year,
        datasets_count=0,
        ai_messages_count=0,
        reports_count=0
    )
    db.add(usage2)
    
    # Should raise integrity error
    with pytest.raises(Exception):
        db.commit()


def test_check_usage_limit_free_tier_dataset(db, test_user):
    """Test usage limit check for free tier datasets."""
    # Create usage with 4 datasets (limit is 5)
    usage = get_or_create_usage(db, test_user.id)
    usage.datasets_count = 4
    db.commit()
    
    # Should allow 5th dataset
    can_proceed, error = check_usage_limit(db, test_user.id, "dataset")
    assert can_proceed is True
    assert error is None
    
    # Increment to 5
    usage.datasets_count = 5
    db.commit()
    
    # Should block 6th dataset
    can_proceed, error = check_usage_limit(db, test_user.id, "dataset")
    assert can_proceed is False
    assert "limit" in error.lower()


def test_check_usage_limit_pro_tier_unlimited(db, test_pro_user):
    """Test that pro tier has unlimited datasets."""
    # Create usage with 100 datasets
    usage = get_or_create_usage(db, test_pro_user.id)
    usage.datasets_count = 100
    db.commit()
    
    # Should still allow more
    can_proceed, error = check_usage_limit(db, test_pro_user.id, "dataset")
    assert can_proceed is True
    assert error is None


def test_check_usage_limit_ai_messages(db, test_user):
    """Test usage limit check for AI messages."""
    # Create usage with 49 messages (limit is 50)
    usage = get_or_create_usage(db, test_user.id)
    usage.ai_messages_count = 49
    db.commit()
    
    # Should allow 50th message
    can_proceed, error = check_usage_limit(db, test_user.id, "ai_message")
    assert can_proceed is True
    
    # Increment to 50
    usage.ai_messages_count = 50
    db.commit()
    
    # Should block 51st message
    can_proceed, error = check_usage_limit(db, test_user.id, "ai_message")
    assert can_proceed is False


def test_check_usage_limit_reports(db, test_user):
    """Test usage limit check for reports."""
    # Create usage with 2 reports (limit is 3)
    usage = get_or_create_usage(db, test_user.id)
    usage.reports_count = 2
    db.commit()
    
    # Should allow 3rd report
    can_proceed, error = check_usage_limit(db, test_user.id, "report")
    assert can_proceed is True
    
    # Increment to 3
    usage.reports_count = 3
    db.commit()
    
    # Should block 4th report
    can_proceed, error = check_usage_limit(db, test_user.id, "report")
    assert can_proceed is False


def test_increment_usage_dataset(db, test_user):
    """Test incrementing dataset usage."""
    usage = get_or_create_usage(db, test_user.id)
    initial_count = usage.datasets_count
    
    success = increment_usage(db, test_user.id, "dataset")
    assert success is True
    
    db.refresh(usage)
    assert usage.datasets_count == initial_count + 1


def test_increment_usage_ai_message(db, test_user):
    """Test incrementing AI message usage."""
    usage = get_or_create_usage(db, test_user.id)
    initial_count = usage.ai_messages_count
    
    success = increment_usage(db, test_user.id, "ai_message")
    assert success is True
    
    db.refresh(usage)
    assert usage.ai_messages_count == initial_count + 1


def test_increment_usage_report(db, test_user):
    """Test incrementing report usage."""
    usage = get_or_create_usage(db, test_user.id)
    initial_count = usage.reports_count
    
    success = increment_usage(db, test_user.id, "report")
    assert success is True
    
    db.refresh(usage)
    assert usage.reports_count == initial_count + 1


def test_increment_usage_invalid_type(db, test_user):
    """Test incrementing with invalid resource type."""
    success = increment_usage(db, test_user.id, "invalid_type")
    assert success is False


def test_get_usage_stats_free_tier(db, test_user):
    """Test getting usage stats for free tier user."""
    # Set some usage
    usage = get_or_create_usage(db, test_user.id)
    usage.datasets_count = 3
    usage.ai_messages_count = 25
    usage.reports_count = 1
    db.commit()
    
    stats = get_usage_stats(db, test_user.id)
    
    assert stats["tier"] == "free"
    assert stats["datasets"]["current"] == 3
    assert stats["datasets"]["limit"] == 5
    assert stats["datasets"]["unlimited"] is False
    assert stats["ai_messages"]["current"] == 25
    assert stats["ai_messages"]["limit"] == 50
    assert stats["reports"]["current"] == 1
    assert stats["reports"]["limit"] == 3


def test_get_usage_stats_pro_tier(db, test_pro_user):
    """Test getting usage stats for pro tier user."""
    # Set some usage
    usage = get_or_create_usage(db, test_pro_user.id)
    usage.datasets_count = 100
    usage.ai_messages_count = 500
    usage.reports_count = 50
    db.commit()
    
    stats = get_usage_stats(db, test_pro_user.id)
    
    assert stats["tier"] == "pro"
    assert stats["datasets"]["current"] == 100
    assert stats["datasets"]["limit"] == -1
    assert stats["datasets"]["unlimited"] is True
    assert stats["ai_messages"]["unlimited"] is True
    assert stats["reports"]["unlimited"] is True


def test_reset_monthly_usage(db, test_user, test_pro_user):
    """Test resetting monthly usage for all users."""
    # Set usage for both users
    usage1 = get_or_create_usage(db, test_user.id)
    usage1.datasets_count = 5
    usage1.ai_messages_count = 50
    usage1.reports_count = 3
    
    usage2 = get_or_create_usage(db, test_pro_user.id)
    usage2.datasets_count = 100
    usage2.ai_messages_count = 500
    usage2.reports_count = 50
    
    db.commit()
    
    # Reset usage
    reset_count = reset_monthly_usage(db)
    
    # Verify counts were reset
    assert reset_count == 2
    
    db.refresh(usage1)
    db.refresh(usage2)
    
    assert usage1.datasets_count == 0
    assert usage1.ai_messages_count == 0
    assert usage1.reports_count == 0
    
    assert usage2.datasets_count == 0
    assert usage2.ai_messages_count == 0
    assert usage2.reports_count == 0


def test_reset_monthly_usage_creates_new_records(db, test_user):
    """Test that reset creates new records for current month."""
    # Don't create any usage record initially
    
    # Reset usage (should create new record for current month)
    reset_count = reset_monthly_usage(db)
    
    # Verify record was created
    current_month = get_current_month_year()
    usage = db.query(UsageTracking).filter(
        UsageTracking.user_id == str(test_user.id),
        UsageTracking.month_year == current_month
    ).first()
    
    assert usage is not None
    assert usage.datasets_count == 0
    assert usage.ai_messages_count == 0
    assert usage.reports_count == 0


def test_user_tier_enum_validation(db):
    """Test that user tier uses enum validation."""
    # Valid tier
    user = User(
        email="enum@example.com",
        username="enumuser",
        hashed_password="hashed",
        tier=UserTier.PRO
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.tier == UserTier.PRO
    assert user.tier.value == "pro"


def test_user_tier_default_is_free(db):
    """Test that default tier is FREE."""
    user = User(
        email="default@example.com",
        username="defaultuser",
        hashed_password="hashed"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.tier == UserTier.FREE
