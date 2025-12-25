# backend/utils/sentry_integration.py
"""
Sentry integration for error tracking and monitoring.
Provides centralized error logging and performance monitoring.
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from typing import Optional, Dict, Any

from config import settings


def init_sentry() -> bool:
    """
    Initialize Sentry SDK for error tracking.
    
    Returns:
        bool: True if Sentry was initialized, False if DSN not configured
    """
    if not settings.SENTRY_DSN:
        print("Sentry DSN not configured - error tracking disabled")
        return False
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=f"iops-backend@{settings.VERSION}",
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        # Don't send PII by default
        send_default_pii=False,
        # Attach stack traces to messages
        attach_stacktrace=True,
        # Filter out health check endpoints from performance monitoring
        before_send_transaction=_filter_transactions,
    )
    
    print(f"Sentry initialized for environment: {settings.SENTRY_ENVIRONMENT}")
    return True


def _filter_transactions(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter out noisy transactions like health checks.
    """
    transaction_name = event.get("transaction", "")
    
    # Skip health check endpoints
    if transaction_name in ["/health", "/api/health", "/api/health/detailed"]:
        return None
    
    return event


def capture_exception(error: Exception, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Capture an exception and send to Sentry.
    
    Args:
        error: The exception to capture
        context: Additional context to attach to the error
        
    Returns:
        The Sentry event ID if captured, None otherwise
    """
    if not settings.SENTRY_DSN:
        return None
    
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        
        return sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Capture a message and send to Sentry.
    
    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
        context: Additional context to attach
        
    Returns:
        The Sentry event ID if captured, None otherwise
    """
    if not settings.SENTRY_DSN:
        return None
    
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        
        return sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: Optional[str] = None, tier: Optional[str] = None) -> None:
    """
    Set user context for Sentry events.
    
    Args:
        user_id: The user's ID
        email: The user's email (optional)
        tier: The user's subscription tier (optional)
    """
    if not settings.SENTRY_DSN:
        return
    
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "tier": tier
    })


def clear_user_context() -> None:
    """Clear the current user context."""
    if settings.SENTRY_DSN:
        sentry_sdk.set_user(None)


def add_breadcrumb(
    message: str,
    category: str = "custom",
    level: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Add a breadcrumb for debugging context.
    
    Args:
        message: Description of the breadcrumb
        category: Category for grouping (e.g., "auth", "database", "api")
        level: Log level
        data: Additional data to attach
    """
    if not settings.SENTRY_DSN:
        return
    
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
