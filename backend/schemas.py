# backend/schemas.py
"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

# ============= Authentication Schemas =============

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str

class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: int
    uuid: str
    email: str
    username: str
    full_name: Optional[str]
    tier: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    profile_picture_url: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    profile_picture_url: Optional[str] = None

class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for resetting password with token"""
    token: str
    new_password: str = Field(..., min_length=8)

class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str

# ============= Dataset Schemas =============

class DatasetResponse(BaseModel):
    """Schema for dataset response"""
    id: int
    session_id: str
    filename: str
    upload_timestamp: datetime
    rows: Optional[int]
    columns: Optional[int]
    file_size: Optional[int]
    
    class Config:
        from_attributes = True

class DatasetListResponse(BaseModel):
    """Schema for list of datasets"""
    datasets: list[DatasetResponse]
    total: int

# ============= Experiment Schemas =============

class ExperimentResponse(BaseModel):
    """Schema for experiment response"""
    id: int
    session_id: str
    dataset_name: str
    timestamp: datetime
    rows: Optional[int]
    columns: Optional[int]
    insights_generated: bool
    report_generated: bool
    status: str
    
    class Config:
        from_attributes = True

# ============= Generic Response Schemas =============

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    status_code: int

# ============= Usage Tracking Schemas =============

class UsageStatsResponse(BaseModel):
    """Schema for usage statistics response"""
    tier: str
    month_year: str
    datasets: dict
    ai_messages: dict
    reports: dict
    
    class Config:
        from_attributes = True

class UsageTrackingResponse(BaseModel):
    """Schema for usage tracking record"""
    id: str
    user_id: str
    month_year: str
    datasets_count: int
    ai_messages_count: int
    reports_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
