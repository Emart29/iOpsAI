# Error Logging and Monitoring Setup

This document describes how to set up error logging and monitoring for the iOps backend.

## 1. Sentry Error Tracking

Sentry provides real-time error tracking and performance monitoring.

### Setup Steps

1. **Create a Sentry Account**
   - Go to [sentry.io](https://sentry.io/) and create a free account
   - Create a new project and select "FastAPI" as the platform

2. **Get Your DSN**
   - Go to Project Settings > Client Keys (DSN)
   - Copy the DSN URL

3. **Configure Environment Variables**
   ```bash
   SENTRY_DSN=https://your-key@sentry.io/your-project-id
   SENTRY_ENVIRONMENT=production  # or development, staging
   SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions for performance monitoring
   SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% for profiling
   ```

### Features Enabled

- **Error Tracking**: All unhandled exceptions are automatically captured
- **Performance Monitoring**: API endpoint response times and database queries
- **User Context**: User ID and tier are attached to errors (when authenticated)
- **Breadcrumbs**: Automatic logging of events leading up to errors

### Manual Error Capture

```python
from utils.sentry_integration import capture_exception, capture_message

# Capture an exception with context
try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={"user_id": user_id, "operation": "risky"})

# Capture a message
capture_message("Important event occurred", level="info", context={"data": "value"})
```

## 2. UptimeRobot Monitoring

UptimeRobot monitors your application's availability and alerts you when it goes down.

### Setup Steps

1. **Create an UptimeRobot Account**
   - Go to [uptimerobot.com](https://uptimerobot.com/) and create a free account

2. **Add a New Monitor**
   - Click "Add New Monitor"
   - Select "HTTP(s)" as the monitor type
   - Enter your backend URL: `https://your-backend-url.com/health`
   - Set monitoring interval (5 minutes recommended for free tier)

3. **Configure Alerts**
   - Add your email for downtime notifications
   - Optionally add Slack, Discord, or other integrations

### Available Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Simple health check | `{"status": "healthy"}` |
| `/api/health` | Alternative path | `{"status": "healthy"}` |
| `/api/health/detailed` | Full component status | Detailed JSON with DB, storage, etc. |
| `/api/health/ready` | Kubernetes readiness | `{"ready": true/false}` |
| `/api/health/live` | Kubernetes liveness | `{"alive": true}` |

### Recommended Monitors

1. **Primary Health Check**: Monitor `/health` every 5 minutes
2. **Detailed Health**: Monitor `/api/health/detailed` every 15 minutes (for dashboards)

## 3. Automated Database Backups

Daily automated backups protect against data loss.

### Setup Steps

1. **Enable Backups**
   ```bash
   BACKUP_ENABLED=true
   BACKUP_DIR=./backups
   BACKUP_RETENTION_DAYS=7
   ```

2. **Schedule the Backup Job**

   **Option A: System Cron (Linux/Mac)**
   ```bash
   # Run daily at 2 AM
   0 2 * * * cd /path/to/backend && python cron_backup.py >> /var/log/iops-backup.log 2>&1
   ```

   **Option B: Render Cron Jobs**
   - Go to your Render dashboard
   - Create a new "Cron Job" service
   - Set the command: `python cron_backup.py`
   - Set the schedule: `0 2 * * *` (daily at 2 AM UTC)

   **Option C: Railway Cron**
   - Use Railway's cron job feature with the same command

### Backup Types

- **SQLite**: Creates a copy of the database file
- **PostgreSQL**: Uses `pg_dump` to create a SQL dump

### Manual Backup

```python
from utils.backup import backup_manager

# Create a backup
backup_path = backup_manager.create_backup()

# List all backups
backups = backup_manager.list_backups()

# Get backup status
status = backup_manager.get_backup_status()
```

### Backup Retention

Backups older than `BACKUP_RETENTION_DAYS` are automatically deleted during the daily backup job.

## 4. Production Checklist

Before going to production, ensure:

- [ ] Sentry DSN is configured
- [ ] UptimeRobot monitor is active
- [ ] Backup job is scheduled
- [ ] Alert notifications are configured (email, Slack, etc.)
- [ ] `SENTRY_ENVIRONMENT` is set to `production`
- [ ] `BACKUP_ENABLED` is set to `true`

## 5. Troubleshooting

### Sentry Not Receiving Events

1. Check that `SENTRY_DSN` is correctly set
2. Verify the DSN format: `https://key@sentry.io/project-id`
3. Check Sentry project settings for any rate limits

### Backups Not Running

1. Verify `BACKUP_ENABLED=true`
2. Check that the backup directory is writable
3. For PostgreSQL, ensure `pg_dump` is installed
4. Check cron job logs for errors

### Health Check Failing

1. Check database connectivity
2. Verify storage directory permissions
3. Check application logs for startup errors
