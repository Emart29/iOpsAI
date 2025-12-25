#!/usr/bin/env python3
# backend/cron_backup.py
"""
Cron job script for automated daily database backups.

Usage:
    python cron_backup.py

This script should be scheduled to run daily via:
- System cron: 0 2 * * * cd /path/to/backend && python cron_backup.py
- Render/Railway cron jobs
- Or any other scheduler

The script will:
1. Create a database backup (SQLite or PostgreSQL)
2. Clean up backups older than the retention period
3. Log results and send alerts on failure
"""
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run the daily backup routine."""
    logger.info("Starting daily backup job...")
    
    try:
        from utils.backup import run_daily_backup, backup_manager
        from utils.sentry_integration import capture_exception, capture_message
        from config import settings
        
        # Check if backups are enabled
        if not settings.BACKUP_ENABLED:
            logger.info("Backups are disabled. Set BACKUP_ENABLED=true to enable.")
            return
        
        # Run backup
        result = run_daily_backup()
        
        if result["error"]:
            logger.error(f"Backup failed: {result['error']}")
            # Send alert to Sentry
            capture_message(
                f"Daily backup failed: {result['error']}",
                level="error",
                context=result
            )
            sys.exit(1)
        
        if result["backup_created"]:
            logger.info(f"Backup created successfully: {result['backup_path']}")
        else:
            logger.warning("No backup was created")
        
        if result["old_backups_deleted"] > 0:
            logger.info(f"Cleaned up {result['old_backups_deleted']} old backup(s)")
        
        # Log backup status
        status = backup_manager.get_backup_status()
        logger.info(f"Backup status: {status['backup_count']} backups, "
                   f"{status['total_size_bytes'] / 1024 / 1024:.2f} MB total")
        
        logger.info("Daily backup job completed successfully")
        
    except Exception as e:
        logger.error(f"Backup job failed with exception: {e}")
        try:
            from utils.sentry_integration import capture_exception
            capture_exception(e, context={"job": "daily_backup"})
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
