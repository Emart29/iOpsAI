# backend/tests/test_cron_reset.py
"""
Test the cron job script for resetting monthly usage.
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, UsageTracking, UserTier
from utils.usage_tracking import reset_monthly_usage, get_or_create_usage


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


def test_cron_reset_with_multiple_users(db):
    """Test that cron job resets usage for multiple users."""
    # Create multiple users
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password="hashed",
            tier=UserTier.FREE if i < 3 else UserTier.PRO
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    
    # Set usage for all users
    for user in users:
        usage = get_or_create_usage(db, user.id)
        usage.datasets_count = 5
        usage.ai_messages_count = 50
        usage.reports_count = 3
    
    db.commit()
    
    # Run reset
    reset_count = reset_monthly_usage(db)
    
    # Verify all users were reset
    assert reset_count == 5
    
    # Verify all usage is zero
    for user in users:
        usage = get_or_create_usage(db, user.id)
        assert usage.datasets_count == 0
        assert usage.ai_messages_count == 0
        assert usage.reports_count == 0


def test_cron_reset_with_no_users(db):
    """Test that cron job handles empty database gracefully."""
    reset_count = reset_monthly_usage(db)
    assert reset_count == 0


def test_cron_reset_idempotent(db):
    """Test that running reset multiple times is safe."""
    # Create user with usage
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        tier=UserTier.FREE
    )
    db.add(user)
    db.commit()
    
    usage = get_or_create_usage(db, user.id)
    usage.datasets_count = 5
    db.commit()
    
    # Run reset twice
    reset_count1 = reset_monthly_usage(db)
    reset_count2 = reset_monthly_usage(db)
    
    # First run should reset 1 user
    assert reset_count1 == 1
    # Second run should reset 0 users (already at zero)
    assert reset_count2 == 0
    
    # Verify usage is still zero
    db.refresh(usage)
    assert usage.datasets_count == 0
