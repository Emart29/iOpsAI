# backend/models.py
"""
Database models for iOps application
Includes User, Dataset, Experiment, and other entities

This file contains both legacy models (for backward compatibility)
and new models aligned with the MVP spec.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, BigInteger, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class UserTier(str, enum.Enum):
    """User subscription tiers"""
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


def get_uuid_column():
    """Return UUID column that works with both PostgreSQL and SQLite."""
    return String(36)


# ============================================================================
# NEW MODELS (MVP Spec - Phase 1 & 2)
# ============================================================================

class UsageTracking(Base):
    """Monthly usage tracking per user for tier limits enforcement."""
    __tablename__ = "usage_tracking"

    id = Column(get_uuid_column(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(get_uuid_column(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    month_year = Column(String(7), nullable=False)
    datasets_count = Column(Integer, default=0, nullable=False)
    ai_messages_count = Column(Integer, default=0, nullable=False)
    reports_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="usage_records")

    __table_args__ = (
        UniqueConstraint('user_id', 'month_year', name='uq_user_month'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<UsageTracking(user_id='{self.user_id}', month='{self.month_year}')>"


class Analysis(Base):
    """Analysis workflows and results (new MVP model)."""
    __tablename__ = "analyses"

    id = Column(get_uuid_column(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(get_uuid_column(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dataset_id = Column(get_uuid_column(), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True)
    config = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    status = Column(String(50), default='draft', nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="analyses")
    dataset = relationship("Dataset", back_populates="analyses")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")

    __table_args__ = ({'extend_existing': True})

    def __repr__(self):
        return f"<Analysis(name='{self.name}', status='{self.status}')>"


class Report(Base):
    """Public shareable reports (Phase 2 - Public Report Sharing)."""
    __tablename__ = "reports"

    id = Column(get_uuid_column(), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(get_uuid_column(), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    short_code = Column(String(20), nullable=False, unique=True, index=True)
    is_public = Column(Boolean, default=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    analysis = relationship("Analysis", back_populates="reports")

    __table_args__ = ({'extend_existing': True})

    def __repr__(self):
        return f"<Report(short_code='{self.short_code}', analysis_id='{self.analysis_id}')>"


# ============================================================================
# LEGACY MODELS (Existing - Updated for compatibility)
# ============================================================================

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    tier = Column(Enum(UserTier), default=UserTier.FREE, nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="owner", cascade="all, delete-orphan")
    usage_records = relationship("UsageTracking", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="owner", cascade="all, delete-orphan")

    __table_args__ = ({'extend_existing': True})

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"


class Dataset(Base):
    """Dataset model - now linked to users"""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    rows = Column(Integer)
    columns = Column(Integer)
    file_path = Column(String)
    file_size = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False)
    name = Column(String(255), nullable=True)
    connection_id = Column(get_uuid_column(), nullable=True, index=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="datasets")
    analyses = relationship("Analysis", back_populates="dataset")

    __table_args__ = ({'extend_existing': True})

    def __repr__(self):
        return f"<Dataset(filename='{self.filename}', session_id='{self.session_id}')>"


class Experiment(Base):
    """Experiment tracking"""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rows = Column(Integer)
    columns = Column(Integer)
    insights_generated = Column(Boolean, default=False)
    report_generated = Column(Boolean, default=False)
    status = Column(String, default="active")

    owner = relationship("User", back_populates="experiments")

    def __repr__(self):
        return f"<Experiment(session_id='{self.session_id}', status='{self.status}')>"


class CleaningOperation(Base):
    """Track data cleaning operations"""
    __tablename__ = "cleaning_operations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    operation_type = Column(String)
    column_name = Column(String, nullable=True)
    details = Column(Text)

    def __repr__(self):
        return f"<CleaningOperation(type='{self.operation_type}', session='{self.session_id}')>"


class GeneratedReport(Base):
    """Track generated reports"""
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    report_type = Column(String)
    file_path = Column(String)

    def __repr__(self):
        return f"<GeneratedReport(type='{self.report_type}', session='{self.session_id}')>"


class PasswordResetToken(Base):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used})>"


class EmailVerificationToken(Base):
    """Email verification tokens"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<EmailVerificationToken(user_id={self.user_id}, used={self.used})>"


class RefreshToken(Base):
    """Refresh tokens for JWT authentication"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    def __repr__(self):
        return f"<RefreshToken(user_id={self.user_id}, revoked={self.revoked})>"
