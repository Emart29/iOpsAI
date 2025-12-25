"""
Utility functions for report generation and management.
Includes short code generation for public reports.
"""
import secrets
import string
from sqlalchemy.orm import Session
from models import Report


def generate_short_code(length: int = 8) -> str:
    """
    Generate a cryptographically secure short code using base62 encoding.
    
    Uses the secrets module for cryptographic randomness to ensure
    uniqueness and security. The short code is composed of alphanumeric
    characters (a-z, A-Z, 0-9).
    
    Args:
        length: Length of the short code to generate (default: 8)
        
    Returns:
        A random base62-encoded string of the specified length
        
    Example:
        >>> code = generate_short_code()
        >>> len(code)
        8
        >>> code.isalnum()
        True
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_short_code(db: Session, length: int = 8, max_attempts: int = 100) -> str:
    """
    Generate a unique short code that doesn't already exist in the database.
    
    Generates short codes until one is found that doesn't exist in the reports table.
    Uses exponential backoff strategy: if collisions occur, increases length.
    
    Args:
        db: SQLAlchemy database session
        length: Initial length of the short code (default: 8)
        max_attempts: Maximum number of generation attempts before increasing length
        
    Returns:
        A unique short code that can be safely stored in the database
        
    Raises:
        RuntimeError: If unable to generate unique code after multiple attempts
        
    Example:
        >>> code = generate_unique_short_code(db)
        >>> len(code) >= 8
        True
    """
    attempts = 0
    current_length = length
    
    while attempts < max_attempts:
        short_code = generate_short_code(current_length)
        
        # Check if this short code already exists
        existing = db.query(Report).filter(
            Report.short_code == short_code
        ).first()
        
        if existing is None:
            # Short code is unique
            return short_code
        
        attempts += 1
    
    # If we've hit max attempts, increase length and try again
    # This prevents infinite loops while maintaining uniqueness
    if current_length < 20:
        return generate_unique_short_code(db, length=current_length + 1, max_attempts=max_attempts)
    
    raise RuntimeError(
        f"Unable to generate unique short code after {max_attempts} attempts "
        f"with length {current_length}"
    )
