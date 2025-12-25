# backend/utils/backup.py
"""
Database backup utilities for automated daily backups.
Supports both SQLite and PostgreSQL databases.
"""
import os
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from config import settings

logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Handles database backup operations."""
    
    def __init__(self):
        self.backup_dir = settings.BACKUP_DIR
        self.retention_days = settings.BACKUP_RETENTION_DAYS
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self) -> None:
        """Create backup directory if it doesn't exist."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_backup_filename(self, prefix: str = "backup") -> str:
        """Generate a timestamped backup filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"
    
    def backup_sqlite(self) -> Optional[Path]:
        """
        Create a backup of SQLite database.
        
        Returns:
            Path to the backup file, or None if backup failed
        """
        if settings.IS_POSTGRES:
            logger.warning("backup_sqlite called but database is PostgreSQL")
            return None
        
        source_path = settings.DATABASE_PATH
        if not source_path.exists():
            logger.error(f"SQLite database not found at {source_path}")
            return None
        
        backup_filename = self._generate_backup_filename("sqlite") + ".db"
        backup_path = self.backup_dir / backup_filename
        
        try:
            shutil.copy2(source_path, backup_path)
            logger.info(f"SQLite backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            return None
    
    def backup_postgres(self) -> Optional[Path]:
        """
        Create a backup of PostgreSQL database using pg_dump.
        
        Returns:
            Path to the backup file, or None if backup failed
        """
        if not settings.IS_POSTGRES:
            logger.warning("backup_postgres called but database is SQLite")
            return None
        
        backup_filename = self._generate_backup_filename("postgres") + ".sql"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # pg_dump uses DATABASE_URL environment variable
            result = subprocess.run(
                ["pg_dump", "-f", str(backup_path), settings.DATABASE_URL],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"pg_dump failed: {result.stderr}")
                return None
            
            logger.info(f"PostgreSQL backup created: {backup_path}")
            return backup_path
            
        except subprocess.TimeoutExpired:
            logger.error("PostgreSQL backup timed out")
            return None
        except FileNotFoundError:
            logger.error("pg_dump not found - ensure PostgreSQL client tools are installed")
            return None
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            return None
    
    def create_backup(self) -> Optional[Path]:
        """
        Create a database backup based on the current database type.
        
        Returns:
            Path to the backup file, or None if backup failed
        """
        if not settings.BACKUP_ENABLED:
            logger.info("Backups are disabled")
            return None
        
        if settings.IS_POSTGRES:
            return self.backup_postgres()
        else:
            return self.backup_sqlite()
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period.
        
        Returns:
            Number of backups deleted
        """
        if not self.backup_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file():
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    try:
                        backup_file.unlink()
                        logger.info(f"Deleted old backup: {backup_file}")
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Failed to delete backup {backup_file}: {e}")
        
        return deleted_count
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup info dictionaries
        """
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_file in sorted(self.backup_dir.iterdir(), reverse=True):
            if backup_file.is_file():
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return backups
    
    def get_backup_status(self) -> Dict[str, Any]:
        """
        Get current backup status and statistics.
        
        Returns:
            Dictionary with backup status information
        """
        backups = self.list_backups()
        total_size = sum(b["size_bytes"] for b in backups)
        
        return {
            "enabled": settings.BACKUP_ENABLED,
            "backup_dir": str(self.backup_dir),
            "retention_days": self.retention_days,
            "database_type": "postgresql" if settings.IS_POSTGRES else "sqlite",
            "backup_count": len(backups),
            "total_size_bytes": total_size,
            "latest_backup": backups[0] if backups else None
        }


# Singleton instance
backup_manager = DatabaseBackup()


def run_daily_backup() -> Dict[str, Any]:
    """
    Run the daily backup routine.
    This function is designed to be called by a cron job or scheduler.
    
    Returns:
        Dictionary with backup results
    """
    result = {
        "timestamp": datetime.now().isoformat(),
        "backup_created": False,
        "backup_path": None,
        "old_backups_deleted": 0,
        "error": None
    }
    
    try:
        # Create new backup
        backup_path = backup_manager.create_backup()
        if backup_path:
            result["backup_created"] = True
            result["backup_path"] = str(backup_path)
        
        # Cleanup old backups
        deleted = backup_manager.cleanup_old_backups()
        result["old_backups_deleted"] = deleted
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Daily backup failed: {e}")
    
    return result
