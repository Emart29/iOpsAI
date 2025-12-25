# Usage Tracking Middleware

This document explains how to use the usage tracking middleware to enforce tier limits on datasets, AI messages, and reports.

## Overview

The usage tracking middleware provides three dependency functions that can be used in FastAPI endpoints to:
1. Check if the user has reached their tier limit for a resource
2. Increment the usage counter if the limit is not reached
3. Return a 403 error with upgrade prompt if the limit is exceeded

## Available Dependencies

### 1. `track_dataset_usage`
Use this dependency for endpoints that upload or create datasets.

### 2. `track_ai_message_usage`
Use this dependency for endpoints that send AI messages or chat interactions.

### 3. `track_report_usage`
Use this dependency for endpoints that create public reports.

## How to Use

### Basic Usage

Import the middleware dependency and add it to your endpoint:

```python
from fastapi import APIRouter, Depends
from models import User
from middleware import track_dataset_usage

router = APIRouter(prefix="/api", tags=["datasets"])

@router.post("/datasets")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(track_dataset_usage)
):
    # Your endpoint logic here
    # The middleware has already:
    # 1. Checked if the user can upload another dataset
    # 2. Incremented their usage counter
    # 3. Returned the authenticated user
    
    # If we reach this point, the user is allowed to proceed
    return {"message": "Dataset uploaded successfully"}
```

### Example: Dataset Upload Endpoint

```python
# backend/routers/datasets.py
from fastapi import APIRouter, UploadFile, File, Depends
from models import User
from middleware import track_dataset_usage
from utils.upload_handler import process_upload_file

router = APIRouter(prefix="/api", tags=["datasets"])

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(track_dataset_usage)
):
    """
    Upload a CSV file and create a new session.
    Enforces tier limits on dataset uploads.
    """
    # Process the upload
    result = await process_upload_file(file, enhanced=False)
    
    # Associate with user
    result["user_id"] = current_user.id
    
    return result
```

### Example: AI Chat Endpoint

```python
# backend/routers/ai.py
from fastapi import APIRouter, Body, Depends
from typing import Dict, Any
from models import User
from middleware import track_ai_message_usage
from utils.ai_helpers import chat_with_data

router = APIRouter(prefix="/api", tags=["ai"])

@router.post("/chat")
async def chat_with_sight(
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(track_ai_message_usage)
):
    """
    Chat with Sight AI about the dataset.
    Enforces tier limits on AI messages.
    """
    message = body.get("message", "").strip()
    session_id = body.get("session_id")
    
    if not message or not session_id:
        raise HTTPException(400, "message and session_id are required")
    
    # Process the chat message
    response = chat_with_data(df, message, chat_history, filename)
    
    return {"response": response}
```

### Example: Report Creation Endpoint

```python
# backend/routers/reports.py
from fastapi import APIRouter, Body, Depends
from typing import Dict, Any
from models import User
from middleware import track_report_usage

router = APIRouter(prefix="/api", tags=["reports"])

@router.post("/reports")
async def create_public_report(
    body: Dict[str, Any] = Body(...),
    current_user: User = Depends(track_report_usage)
):
    """
    Create a public shareable report.
    Enforces tier limits on report creation.
    """
    analysis_id = body.get("analysis_id")
    
    # Create the report
    report = create_report(analysis_id, current_user.id)
    
    return {"report_url": f"/r/{report.short_code}"}
```

## Error Response Format

When a user exceeds their tier limit, the middleware returns a 403 error with the following format:

```json
{
  "detail": {
    "error": {
      "code": "USAGE_LIMIT_EXCEEDED",
      "message": "You've reached your monthly dataset limit (5/5). Please upgrade your plan.",
      "details": {
        "resource_type": "dataset",
        "tier": "free",
        "upgrade_url": "/pricing"
      }
    }
  }
}
```

## Frontend Integration

The frontend should handle 403 errors and display an upgrade prompt:

```typescript
try {
  const response = await fetch('/api/datasets', {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 403) {
    const error = await response.json();
    if (error.detail?.error?.code === 'USAGE_LIMIT_EXCEEDED') {
      // Show upgrade modal
      showUpgradeModal(error.detail.error.message);
    }
  }
} catch (error) {
  console.error('Upload failed:', error);
}
```

## Tier Limits

The following limits are enforced:

### Free Tier
- Datasets: 5 per month
- AI Messages: 50 per month
- Reports: 3 per month

### Pro Tier
- Datasets: Unlimited
- AI Messages: Unlimited
- Reports: Unlimited

### Team Tier
- Datasets: Unlimited
- AI Messages: Unlimited
- Reports: Unlimited

### Enterprise Tier
- Datasets: Unlimited
- AI Messages: Unlimited
- Reports: Unlimited

## Testing

The middleware includes comprehensive tests in `backend/tests/test_usage_middleware.py`:

```bash
# Run middleware tests
python -m pytest backend/tests/test_usage_middleware.py -v

# Run all usage tracking tests
python -m pytest backend/tests/test_usage*.py -v
```

## Implementation Details

### Internal Flow

1. **Authentication**: The middleware depends on `get_current_user`, so the user must be authenticated
2. **Limit Check**: Calls `check_usage_limit()` to verify if the user can proceed
3. **Error Handling**: If limit is reached, raises HTTPException with 403 status
4. **Usage Increment**: If limit is not reached, calls `increment_usage()` to update the counter
5. **Return User**: Returns the authenticated user object for use in the endpoint

### Database Operations

The middleware performs the following database operations:
- Queries the user's tier from the `users` table
- Gets or creates a usage record in the `usage_tracking` table
- Increments the appropriate counter (datasets_count, ai_messages_count, or reports_count)
- Commits the transaction

### Performance Considerations

- The middleware makes 2-3 database queries per request
- Usage records are cached in the session for the current month
- Consider adding Redis caching for high-traffic scenarios

## Migration Guide

To add usage tracking to existing endpoints:

1. Import the appropriate middleware function:
   ```python
   from middleware import track_dataset_usage  # or track_ai_message_usage, track_report_usage
   ```

2. Add the dependency to your endpoint:
   ```python
   async def my_endpoint(
       current_user: User = Depends(track_dataset_usage)
   ):
   ```

3. Remove any existing `current_user: User = Depends(get_current_user)` if present (the middleware already includes authentication)

4. Test the endpoint with a free tier user at their limit to verify the 403 error is returned

## Troubleshooting

### Issue: "User not found" error
**Solution**: Ensure the user is authenticated and the JWT token is valid

### Issue: Usage counter not incrementing
**Solution**: Check that the database transaction is being committed properly

### Issue: Pro tier users getting blocked
**Solution**: Verify that the user's tier is set correctly in the database and that TIER_LIMITS in config.py has -1 for unlimited resources

### Issue: Usage not resetting monthly
**Solution**: Ensure the cron job for `reset_monthly_usage()` is running on the 1st of each month

## Related Files

- `backend/middleware/usage_tracking.py` - Middleware implementation
- `backend/utils/usage_tracking.py` - Core usage tracking utilities
- `backend/models.py` - User and UsageTracking models
- `backend/config.py` - Tier limits configuration
- `backend/tests/test_usage_middleware.py` - Middleware tests
- `backend/tests/test_usage_tracking.py` - Utility tests
