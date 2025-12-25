# backend/routers/health.py
"""
Health check endpoints for monitoring and uptime tracking.
Designed for use with UptimeRobot and similar monitoring services.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from typing import Dict, Any
import sys

from database import get_db
from config import settings
from storage import storage

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint for basic uptime monitoring.
    Returns 200 OK if the service is running.
    
    This endpoint is designed for UptimeRobot and similar services
    that just need to verify the service is responding.
    """
    return {"status": "healthy"}


@router.get("/api/health")
async def api_health_check() -> Dict[str, str]:
    """
    API health check endpoint (alternative path).
    """
    return {"status": "healthy"}


@router.get("/api/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with component status.
    
    Checks:
    - Database connectivity
    - Storage system
    - Memory/system info
    
    Returns detailed status for debugging and monitoring dashboards.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "postgresql" if settings.IS_POSTGRES else "sqlite"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check storage
    try:
        sessions = storage.list_sessions()
        health_status["components"]["storage"] = {
            "status": "healthy",
            "active_sessions": len(sessions)
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["storage"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # System info
    health_status["components"]["system"] = {
        "python_version": sys.version,
        "debug_mode": settings.DEBUG
    }
    
    # Sentry status
    health_status["components"]["error_tracking"] = {
        "enabled": bool(settings.SENTRY_DSN),
        "environment": settings.SENTRY_ENVIRONMENT if settings.SENTRY_DSN else None
    }
    
    # Backup status
    health_status["components"]["backups"] = {
        "enabled": settings.BACKUP_ENABLED,
        "retention_days": settings.BACKUP_RETENTION_DAYS if settings.BACKUP_ENABLED else None
    }
    
    return health_status


@router.get("/api/health/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe.
    Returns 200 only if the service is ready to accept traffic.
    """
    try:
        # Verify database is accessible
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        return {"ready": False, "error": str(e)}


@router.get("/api/health/live")
async def liveness_check() -> Dict[str, bool]:
    """
    Kubernetes-style liveness probe.
    Returns 200 if the service is alive (even if not fully ready).
    """
    return {"alive": True}
