# backend/config.py
"""Configuration settings for the iOps application.
Loaded from environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from urllib.parse import urlparse

class Settings:
    # Core FastAPI settings
    APP_NAME: str = "iOps Data Science Copilot"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    VERSION: str = "2.0.0"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, staging, production

    # Database
    _raw_database_url: str = os.getenv("DATABASE_URL", "sqlite:///./iops.db")
    
    # Handle Render's postgres:// URL format (convert to postgresql://)
    @property
    def DATABASE_URL(self) -> str:
        url = self._raw_database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    # Check if using PostgreSQL
    @property
    def IS_POSTGRES(self) -> bool:
        return self.DATABASE_URL.startswith("postgresql://")
    
    # Extract filesystem path for SQLite DB (used by storage module)
    @property
    def DATABASE_PATH(self) -> Path:
        if self.IS_POSTGRES:
            return Path("./data")  # Fallback path for file storage
        return Path(self._raw_database_url.replace("sqlite:///", ""))

    # File handling
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./temp_uploads"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50 MB
    ALLOWED_EXTENSIONS: set = {"csv", "xls", "xlsx", "json"}

    # Groq AI integration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # CORS origins for local dev and production
    @property
    def CORS_ORIGINS_LIST(self) -> list:
        """Parse CORS_ORIGINS string into a list"""
        origins_str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000",
        )
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    )

    # Session management
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "86400"))  # seconds (24h)

    # Authentication & JWT Settings (Phase 1)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-min-32-chars-long-please")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Email Settings (Phase 1)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "iOps <onboarding@resend.dev>")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Password Reset Token Expiration
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    SEND_VERIFICATION_EMAILS: bool = os.getenv("SEND_VERIFICATION_EMAILS", "false").lower() == "true"
    
    # Error Monitoring (Sentry)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", ENVIRONMENT)
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))  # 10% of transactions
    SENTRY_PROFILES_SAMPLE_RATE: float = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))  # 10% of profiled transactions
    
    # Database Backup Settings
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "false").lower() == "true"
    BACKUP_DIR: Path = Path(os.getenv("BACKUP_DIR", "./backups"))
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))

    # Tier Limits (Phase 1)
    TIER_LIMITS = {
        "free": {
            "datasets_per_month": 5,
            "ai_messages_per_month": 50,
            "reports_per_month": 3,
            "collaborators_per_analysis": 3,
            "data_connections": 5,
            "chart_types": ["line", "bar", "scatter", "pie"],
            "branding": "full"
        },
        "pro": {
            "datasets_per_month": -1,  # unlimited
            "ai_messages_per_month": -1,
            "reports_per_month": -1,
            "collaborators_per_analysis": 3,
            "data_connections": 5,
            "chart_types": "all",
            "branding": "minimal"
        },
        "team": {
            "datasets_per_month": -1,
            "ai_messages_per_month": -1,
            "reports_per_month": -1,
            "collaborators_per_analysis": -1,
            "data_connections": 10,
            "chart_types": "all",
            "branding": "minimal"
        },
        "enterprise": {
            "datasets_per_month": -1,
            "ai_messages_per_month": -1,
            "reports_per_month": -1,
            "collaborators_per_analysis": -1,
            "data_connections": -1,
            "chart_types": "all",
            "branding": "none"
        }
    }

settings = Settings()

# Validate that the Groq API key is provided
if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "YOUR_GROQ_API_KEY":
    raise EnvironmentError("GROQ_API_KEY is missing or still set to the placeholder. Please add it to .env.")