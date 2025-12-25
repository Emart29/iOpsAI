# backend/routers/auth.py
"""
Authentication router for user registration, login, and password management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import User, PasswordResetToken, EmailVerificationToken, RefreshToken
from schemas import (
    UserRegister, UserLogin, Token, TokenRefresh, UserResponse,
    PasswordChange, PasswordResetRequest, PasswordReset,
    EmailVerification, MessageResponse
)
from utils.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, get_current_user, validate_password_strength,
    generate_verification_token, generate_password_reset_token
)
from utils.email_service import email_service
from utils.usage_tracking import get_usage_stats
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - Creates user account
    - Sends verification email
    - Returns success message
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate password strength
    validate_password_strength(user_data.password)
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_pwd,
        is_active=True,
        is_verified=False  # Require email verification
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate verification token
    verification_token = generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    
    token_record = EmailVerificationToken(
        user_id=new_user.id,
        token=verification_token,
        expires_at=expires_at
    )
    db.add(token_record)
    db.commit()
    
    # Send verification email only if enabled
    if settings.RESEND_API_KEY and getattr(settings, "SEND_VERIFICATION_EMAILS", False):
        email_service.send_verification_email(
            email=new_user.email,
            username=new_user.username,
            verification_token=verification_token
        )
    else:
        print("⚙️  Skipping verification email (SEND_VERIFICATION_EMAILS=False)")
    
    return MessageResponse(
        message="Registration successful! Please check your email to verify your account.",
        detail=f"Verification email sent to {new_user.email}"
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT tokens
    
    - Validates credentials
    - Returns access and refresh tokens
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Note: We allow login even if not verified, but some features may be restricted
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Store refresh token in database
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token_record)
    db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(token_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Check if refresh token exists and is not revoked
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token == token_data.refresh_token,
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked refresh token"
            )
        
        # Check if token is expired
        if token_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": user.id, "email": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        # Revoke old refresh token
        token_record.revoked = True
        
        # Store new refresh token
        new_token_record = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_token_record)
        db.commit()
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout(
    token_data: TokenRefresh,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token
    """
    # Revoke the refresh token
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if token_record:
        token_record.revoked = True
        db.commit()
    
    return MessageResponse(message="Logged out successfully")

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(verification: EmailVerification, db: Session = Depends(get_db)):
    """
    Verify user email with token
    """
    # Find token
    token_record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == verification.token,
        EmailVerificationToken.used == False
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Check if token is expired
    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Get user and verify
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_verified = True
    token_record.used = True
    db.commit()
    
    # Send welcome email
    if settings.RESEND_API_KEY:
        email_service.send_welcome_email(
            email=user.email,
            username=user.username
        )
    
    return MessageResponse(
        message="Email verified successfully!",
        detail="You can now access all features."
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request password reset email
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    # Don't reveal if email exists or not (security best practice)
    if not user:
        return MessageResponse(
            message="If the email exists, a password reset link has been sent.",
            detail="Please check your email."
        )
    
    # Generate reset token
    reset_token = generate_password_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    
    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )
    db.add(token_record)
    db.commit()
    
    # Send reset email
    if settings.RESEND_API_KEY:
        email_service.send_password_reset_email(
            email=user.email,
            username=user.username,
            reset_token=reset_token
        )
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent.",
        detail="Please check your email."
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    Reset password with token
    """
    # Find token
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token,
        PasswordResetToken.used == False
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check if token is expired
    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Validate new password
    validate_password_strength(reset_data.new_password)
    
    # Get user and update password
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = hash_password(reset_data.new_password)
    token_record.used = True
    
    # Revoke all refresh tokens for security
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    
    return MessageResponse(
        message="Password reset successfully!",
        detail="Please login with your new password."
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    validate_password_strength(password_data.new_password)
    
    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    
    # Revoke all refresh tokens for security
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    
    return MessageResponse(
        message="Password changed successfully!",
        detail="Please login again with your new password."
    )

@router.get("/usage")
async def get_user_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's usage statistics and tier limits
    
    Returns usage counts and limits for:
    - Datasets uploaded this month
    - AI messages sent this month
    - Public reports created this month
    """
    usage_stats = get_usage_stats(db, current_user.id)
    return usage_stats
