# backend/database.py
"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base

# Get the database URL (handles postgres:// to postgresql:// conversion)
database_url = settings.DATABASE_URL

# Create engine with proper configuration
if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # For PostgreSQL or other databases
    # Use connection pooling for production
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Number of connections to keep open
        max_overflow=10,  # Additional connections when pool is exhausted
        pool_recycle=300,  # Recycle connections after 5 minutes
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
