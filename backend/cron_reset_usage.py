#!/usr/bin/env python3
# backend/cron_reset_usage.py
"""
Cron job script to reset monthly usage counters.
This should be scheduled to run on the 1st of each month at 00:00 UTC.

Usage:
    python cron_reset_usage.py

Cron schedule example (runs at midnight on the 1st of every month):
    0 0 1 * * cd /path/to/backend && python cron_reset_usage.py >> /var/log/iops_usage_reset.log 2>&1
"""
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from utils.usage_tracking import reset_monthly_usage
from datetime import datetime


def main():
    """Main function to reset monthly usage."""
    print(f"[{datetime.utcnow().isoformat()}] Starting monthly usage reset...")
    
    db = SessionLocal()
    try:
        reset_count = reset_monthly_usage(db)
        print(f"[{datetime.utcnow().isoformat()}] Successfully reset usage for {reset_count} users")
        return 0
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] ERROR: Failed to reset usage: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
