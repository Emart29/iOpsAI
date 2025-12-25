# Usage Tracking System

This document describes the usage tracking system for tier management and limit enforcement in the iOps platform.

## Overview

The usage tracking system monitors user resource consumption and enforces tier-based limits on:
- Datasets uploaded per month
- AI messages sent per month
- Public reports created per month

## Components

### 1. Database Models

#### UserTier Enum
```python
class UserTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"
```

#### User Model
- `tier`: Enum field with validation (default: FREE)
- `stripe_customer_id`: Stripe customer identifier
- `stripe_subscription_id`: Stripe subscription identifier
- `is_admin`: Admin flag

#### UsageTracking Model
- `user_id`: Foreign key to users table
- `month_year`: Month in YYYY-MM format
- `datasets_count`: Number of datasets uploaded this month
- `ai_messages_count`: Number of AI messages sent this month
- `reports_count`: Number of public reports created this month
- **Unique constraint**: (user_id, month_year)

### 2. Tier Limits Configuration

Defined in `config.py`:

```python
TIER_LIMITS = {
    "free": {
        "datasets_per_month": 5,
        "ai_messages_per_month": 50,
        "reports_per_month": 3,
        ...
    },
    "pro": {
        "datasets_per_month": -1,  # unlimited
        "ai_messages_per_month": -1,
        "reports_per_month": -1,
        ...
    },
    ...
}
```

Note: `-1` means unlimited.

### 3. Helper Functions

Located in `utils/usage_tracking.py`:

#### `get_or_create_usage(db, user_id, month_year=None)`
Gets existing usage record or creates a new one for the specified month.

**Parameters:**
- `db`: Database session
- `user_id`: User ID (string or integer)
- `month_year`: Optional month in YYYY-MM format (defaults to current month)

**Returns:** UsageTracking object

#### `check_usage_limit(db, user_id, resource_type)`
Checks if user has reached their usage limit for a resource type.

**Parameters:**
- `db`: Database session
- `user_id`: User ID
- `resource_type`: One of "dataset", "ai_message", "report"

**Returns:** Tuple of (can_proceed: bool, error_message: Optional[str])

**Example:**
```python
can_proceed, error = check_usage_limit(db, user_id, "dataset")
if not can_proceed:
    raise HTTPException(status_code=403, detail=error)
```

#### `increment_usage(db, user_id, resource_type)`
Increments the usage counter for a resource type.

**Parameters:**
- `db`: Database session
- `user_id`: User ID
- `resource_type`: One of "dataset", "ai_message", "report"

**Returns:** bool (True if successful)

**Example:**
```python
# After successfully uploading a dataset
increment_usage(db, user_id, "dataset")
```

#### `get_usage_stats(db, user_id)`
Gets current usage statistics with limits for a user.

**Returns:** Dictionary with usage stats:
```python
{
    "tier": "free",
    "month_year": "2024-12",
    "datasets": {
        "current": 3,
        "limit": 5,
        "unlimited": False
    },
    "ai_messages": {...},
    "reports": {...}
}
```

#### `reset_monthly_usage(db)`
Resets usage counters for all users. Called by cron job on the 1st of each month.

**Returns:** int (number of users reset)

### 4. Cron Job

Located in `cron_reset_usage.py`:

**Purpose:** Resets monthly usage counters on the 1st of each month.

**Usage:**
```bash
python backend/cron_reset_usage.py
```

**Cron Schedule Example:**
```bash
# Run at midnight on the 1st of every month
0 0 1 * * cd /path/to/backend && python cron_reset_usage.py >> /var/log/iops_usage_reset.log 2>&1
```

**Alternative Scheduling Options:**
- **Render/Railway:** Use platform's cron job feature
- **Celery Beat:** Schedule as a periodic task
- **GitHub Actions:** Use scheduled workflow
- **Cloud Functions:** Use cloud provider's scheduler (AWS EventBridge, GCP Cloud Scheduler)

## Usage Examples

### In API Endpoints

```python
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from utils.usage_tracking import check_usage_limit, increment_usage

@app.post("/api/datasets")
async def upload_dataset(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user can upload
    can_proceed, error = check_usage_limit(db, current_user.id, "dataset")
    if not can_proceed:
        raise HTTPException(status_code=403, detail=error)
    
    # Process upload...
    dataset = create_dataset(file)
    
    # Increment usage counter
    increment_usage(db, current_user.id, "dataset")
    
    return {"dataset_id": dataset.id}
```

### Getting Usage Stats

```python
from utils.usage_tracking import get_usage_stats

@app.get("/api/users/me/usage")
async def get_my_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stats = get_usage_stats(db, current_user.id)
    return stats
```

## Database Migration

A migration file is provided at `migrations/versions/002_add_usage_tracking_constraint.py`.

**To apply:**
```bash
cd backend
alembic upgrade head
```

This migration:
1. Adds unique constraint on (user_id, month_year) in usage_tracking table
2. Updates tier column to use enum (PostgreSQL only)

## Testing

Comprehensive tests are available in `tests/test_usage_tracking.py`.

**Run tests:**
```bash
pytest backend/tests/test_usage_tracking.py -v
```

**Test coverage:**
- ✅ Creating and retrieving usage records
- ✅ Unique constraint enforcement
- ✅ Usage limit checking for all resource types
- ✅ Free tier limits (5 datasets, 50 AI messages, 3 reports)
- ✅ Pro tier unlimited access
- ✅ Usage increment functionality
- ✅ Monthly usage reset
- ✅ User tier enum validation
- ✅ Usage statistics retrieval

## API Schemas

Response schemas are defined in `schemas.py`:

### UsageStatsResponse
```python
{
    "tier": "free",
    "month_year": "2024-12",
    "datasets": {
        "current": 3,
        "limit": 5,
        "unlimited": false
    },
    "ai_messages": {
        "current": 25,
        "limit": 50,
        "unlimited": false
    },
    "reports": {
        "current": 1,
        "limit": 3,
        "unlimited": false
    }
}
```

## Error Handling

When limits are exceeded, the system returns:
- **Status Code:** 403 Forbidden
- **Error Message:** Descriptive message with current usage and limit
- **Example:** "You've reached your monthly dataset limit (5/5). Please upgrade your plan."

## Future Enhancements

1. **Real-time Usage Updates:** WebSocket notifications when approaching limits
2. **Usage Analytics:** Track usage trends over time
3. **Soft Limits:** Warning notifications at 80% usage
4. **Grace Period:** Allow slight overages with warnings
5. **Usage History:** Store historical usage data for analytics
6. **Custom Limits:** Allow admins to set custom limits per user

## Troubleshooting

### Issue: Unique constraint violation
**Cause:** Attempting to create duplicate usage record for same user/month
**Solution:** Always use `get_or_create_usage()` instead of creating records directly

### Issue: Usage not resetting on 1st of month
**Cause:** Cron job not running
**Solution:** Verify cron job is scheduled and check logs

### Issue: Incorrect tier limits
**Cause:** User tier not properly set or config mismatch
**Solution:** Verify user.tier matches a key in TIER_LIMITS config

## Support

For questions or issues, contact the development team or create an issue in the repository.
