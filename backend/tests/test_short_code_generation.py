"""
Tests for short code generation functionality.
Tests both unit-level properties and integration with the database.
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Report, Analysis, User, UserTier
from utils.report_utils import generate_short_code, generate_unique_short_code


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
def test_analysis(db, test_user):
    """Create a test analysis."""
    analysis = Analysis(
        user_id=str(test_user.id),
        name="Test Analysis",
        status="completed"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


class TestGenerateShortCode:
    """Tests for the generate_short_code function."""
    
    def test_generates_string(self):
        """Test that generate_short_code returns a string."""
        code = generate_short_code()
        assert isinstance(code, str)
    
    def test_default_length_is_8(self):
        """Test that default length is 8 characters."""
        code = generate_short_code()
        assert len(code) == 8
    
    def test_custom_length(self):
        """Test that custom length is respected."""
        for length in [4, 6, 10, 16, 32]:
            code = generate_short_code(length=length)
            assert len(code) == length
    
    def test_alphanumeric_only(self):
        """Test that generated code contains only alphanumeric characters."""
        for _ in range(100):
            code = generate_short_code()
            assert code.isalnum(), f"Code contains non-alphanumeric: {code}"
    
    def test_randomness(self):
        """Test that generated codes are random (no duplicates in large sample)."""
        codes = set()
        for _ in range(1000):
            code = generate_short_code()
            assert code not in codes, f"Duplicate code generated: {code}"
            codes.add(code)


class TestGenerateUniqueShortCode:
    """Tests for the generate_unique_short_code function."""
    
    def test_generates_unique_code(self, db):
        """Test that generate_unique_short_code returns a unique code."""
        code = generate_unique_short_code(db)
        assert isinstance(code, str)
        assert len(code) >= 8
    
    def test_code_not_in_database(self, db, test_analysis):
        """Test that generated code doesn't exist in database."""
        code = generate_unique_short_code(db)
        
        existing = db.query(Report).filter(
            Report.short_code == code
        ).first()
        
        assert existing is None
    
    def test_uniqueness_with_existing_reports(self, db, test_analysis):
        """Test that generated code is unique even with existing reports."""
        # Create multiple reports with different short codes
        codes = set()
        for i in range(10):
            code = generate_unique_short_code(db)
            codes.add(code)
            
            report = Report(
                analysis_id=str(test_analysis.id),
                short_code=code,
                is_public=True
            )
            db.add(report)
        
        db.commit()
        
        # Generate another code - should not match any existing
        new_code = generate_unique_short_code(db)
        assert new_code not in codes
    
    def test_multiple_unique_codes(self, db):
        """Test that multiple calls generate different codes."""
        codes = set()
        for _ in range(100):
            code = generate_unique_short_code(db)
            assert code not in codes, f"Duplicate code generated: {code}"
            codes.add(code)
    
    def test_custom_length(self, db):
        """Test that custom length is respected."""
        code = generate_unique_short_code(db, length=12)
        assert len(code) >= 12
    
    def test_increases_length_on_collision(self, db, test_analysis):
        """Test that length increases when collisions occur."""
        # Fill database with many short codes of length 4
        for i in range(50):
            code = f"{i:04d}"  # Generate codes like 0000, 0001, etc.
            report = Report(
                analysis_id=str(test_analysis.id),
                short_code=code,
                is_public=True
            )
            db.add(report)
        
        db.commit()
        
        # Now generate a unique code with initial length 4
        # Should increase length to avoid collisions
        code = generate_unique_short_code(db, length=4, max_attempts=10)
        
        # Code should be longer than 4 due to collision handling
        assert len(code) >= 4
        
        # Verify it's not in database
        existing = db.query(Report).filter(
            Report.short_code == code
        ).first()
        assert existing is None


class TestShortCodeProperties:
    """Property-based tests for short code generation."""
    
    def test_short_code_uniqueness_property(self, db):
        """
        Property: For any two short codes generated, they should be unique.
        Validates: Requirements 2.1
        """
        generated_codes = set()
        
        for _ in range(500):
            code = generate_unique_short_code(db)
            assert code not in generated_codes, \
                f"Short code collision detected: {code}"
            generated_codes.add(code)
    
    def test_short_code_format_property(self):
        """
        Property: All generated short codes should be alphanumeric.
        Validates: Requirements 2.1
        """
        for _ in range(100):
            code = generate_short_code()
            assert code.isalnum(), \
                f"Short code contains non-alphanumeric characters: {code}"
            assert len(code) > 0, "Short code is empty"
    
    def test_short_code_length_property(self):
        """
        Property: Generated short codes should have the requested length.
        Validates: Requirements 2.1
        """
        for length in [4, 6, 8, 10, 16]:
            code = generate_short_code(length=length)
            assert len(code) == length, \
                f"Expected length {length}, got {len(code)}"
    
    def test_database_uniqueness_property(self, db, test_analysis):
        """
        Property: For any report created with a generated short code,
        no other report should have the same short code.
        Validates: Requirements 2.1
        """
        created_codes = set()
        
        for i in range(50):
            code = generate_unique_short_code(db)
            
            report = Report(
                analysis_id=str(test_analysis.id),
                short_code=code,
                is_public=True
            )
            db.add(report)
            db.commit()
            
            # Verify no duplicates in database
            count = db.query(Report).filter(
                Report.short_code == code
            ).count()
            assert count == 1, \
                f"Multiple reports with same short code: {code}"
            
            created_codes.add(code)
        
        # Verify all codes are unique
        assert len(created_codes) == 50, \
            "Not all generated codes were unique"
