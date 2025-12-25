# Database Schema Documentation

## Overview

This document describes the database schema for the iOps MVP application. The schema is managed using Alembic migrations and supports both PostgreSQL (production) and SQLite (development).

## Core Tables (Phase 1)

### users

Stores user account information and subscription details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID/String(36) | PRIMARY KEY | Unique user identifier |
| email | String(255) | UNIQUE, NOT NULL, INDEXED | User email address |
| password_hash | String(255) | NOT NULL | Bcrypt hashed password |
| full_name | String(255) | NULL | User's full name |
| tier | String(50) | NOT NULL, DEFAULT 'free', INDEXED | Subscription tier (free, pro, team, enterprise) |
| stripe_customer_id | String(255) | NULL, INDEXED | Stripe customer ID |
| stripe_subscription_id | String(255) | NULL | Stripe subscription ID |
| is_admin | Boolean | NOT NULL, DEFAULT false | Admin flag |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_users_email` on `email`
- `idx_users_tier` on `tier`
- `idx_users_stripe_customer_id` on `stripe_customer_id`

**Relationships:**
- One-to-many with `usage_tracking` (CASCADE DELETE)
- One-to-many with `datasets` (CASCADE DELETE)
- One-to-many with `analyses` (CASCADE DELETE)

---

### usage_tracking

Tracks monthly resource usage per user for tier limit enforcement.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID/String(36) | PRIMARY KEY | Unique record identifier |
| user_id | UUID/String(36) | FOREIGN KEY, NOT NULL, INDEXED | Reference to users.id |
| month_year | String(7) | NOT NULL | Month in format 'YYYY-MM' |
| datasets_count | Integer | NOT NULL, DEFAULT 0 | Number of datasets uploaded this month |
| ai_messages_count | Integer | NOT NULL, DEFAULT 0 | Number of AI messages sent this month |
| reports_count | Integer | NOT NULL, DEFAULT 0 | Number of public reports created this month |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Constraints:**
- UNIQUE constraint on `(user_id, month_year)`
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Indexes:**
- `idx_usage_tracking_user_id` on `user_id`
- `idx_usage_tracking_user_month` on `(user_id, month_year)`
- `idx_usage_tracking_month_year` on `month_year`

**Relationships:**
- Many-to-one with `users`

---

### datasets

Stores metadata about uploaded datasets.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID/String(36) | PRIMARY KEY | Unique dataset identifier |
| user_id | UUID/String(36) | FOREIGN KEY, NOT NULL, INDEXED | Reference to users.id |
| name | String(255) | NOT NULL | Dataset name |
| file_path | String(500) | NULL | Path to stored file |
| connection_id | UUID/String(36) | NULL, INDEXED | Reference to data_connections.id (future) |
| row_count | Integer | NULL | Number of rows in dataset |
| column_count | Integer | NULL | Number of columns in dataset |
| size_bytes | BigInteger | NULL | File size in bytes |
| created_at | DateTime | NOT NULL, DEFAULT NOW(), INDEXED | Upload timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Constraints:**
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Indexes:**
- `idx_datasets_user_id` on `user_id`
- `idx_datasets_connection_id` on `connection_id`
- `idx_datasets_created_at` on `created_at`

**Relationships:**
- Many-to-one with `users`
- One-to-many with `analyses`

---

### analyses

Stores analysis workflows and results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID/String(36) | PRIMARY KEY | Unique analysis identifier |
| user_id | UUID/String(36) | FOREIGN KEY, NOT NULL, INDEXED | Reference to users.id |
| name | String(255) | NOT NULL | Analysis name |
| dataset_id | UUID/String(36) | FOREIGN KEY, NULL, INDEXED | Reference to datasets.id |
| config | JSON/Text | NULL | Analysis configuration (JSON) |
| results | JSON/Text | NULL | Analysis results (JSON) |
| status | String(50) | NOT NULL, DEFAULT 'draft', INDEXED | Status (draft, completed, failed) |
| created_at | DateTime | NOT NULL, DEFAULT NOW(), INDEXED | Creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Constraints:**
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- FOREIGN KEY `dataset_id` REFERENCES `datasets(id)` ON DELETE SET NULL

**Indexes:**
- `idx_analyses_user_id` on `user_id`
- `idx_analyses_dataset_id` on `dataset_id`
- `idx_analyses_status` on `status`
- `idx_analyses_created_at` on `created_at`

**Relationships:**
- Many-to-one with `users`
- Many-to-one with `datasets`
- One-to-many with `reports` (CASCADE DELETE)

---

## Phase 2 Tables

### reports

Stores public shareable reports with unique short codes for URL access.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID/String(36) | PRIMARY KEY | Unique report identifier |
| analysis_id | UUID/String(36) | FOREIGN KEY, NOT NULL, INDEXED | Reference to analyses.id |
| short_code | String(20) | UNIQUE, NOT NULL, INDEXED | Base62 encoded short code for public URL |
| is_public | Boolean | NOT NULL, DEFAULT true | Whether report is publicly accessible |
| password_hash | String(255) | NULL | Bcrypt hashed password for protected reports |
| expires_at | DateTime | NULL, INDEXED | Optional expiration timestamp |
| view_count | Integer | NOT NULL, DEFAULT 0 | Number of times report has been viewed |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Report creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Constraints:**
- FOREIGN KEY `analysis_id` REFERENCES `analyses(id)` ON DELETE CASCADE
- UNIQUE constraint on `short_code`

**Indexes:**
- `idx_reports_short_code` on `short_code` (UNIQUE)
- `idx_reports_analysis_id` on `analysis_id`
- `idx_reports_expires_at` on `expires_at`

**Relationships:**
- Many-to-one with `analyses`

**Usage:**
- Public reports are accessible at `/r/:short_code`
- Password-protected reports require verification before viewing
- Expired reports return 410 Gone status
- View count is incremented atomically on each view

---

## Tier Limits

The `tier` column in the `users` table determines resource limits:

| Tier | Datasets/Month | AI Messages/Month | Reports/Month | Collaborators | Data Connections |
|------|----------------|-------------------|---------------|---------------|------------------|
| free | 5 | 50 | 3 | 3 | 5 |
| pro | Unlimited | Unlimited | Unlimited | 3 | 5 |
| team | Unlimited | Unlimited | Unlimited | Unlimited | 10 |
| enterprise | Custom | Custom | Custom | Custom | Custom |

## Future Tables (Phases 3-7)

The following tables will be added in future migrations:

### Phase 3: Embeddable Charts
- `charts` - Chart configurations
- `embed_analytics` - Embed tracking

### Phase 4: Billing
- (Stripe handles most billing data)

### Phase 5: Templates
- `templates` - Reusable analysis templates
- `template_purchases` - Purchase records
- `template_ratings` - User ratings

### Phase 6: Collaboration
- `collaborations` - Collaboration invitations
- `comments` - Chart comments
- `activity_log` - Activity tracking

### Phase 7: Data Connections
- `data_connections` - External data source connections
- `analytics_events` - User behavior tracking

## Migration Management

### Apply Migrations

```bash
# Apply all pending migrations
python migrate.py upgrade

# Apply specific migration
python migrate.py upgrade 001
```

### Rollback Migrations

```bash
# Rollback one migration
python migrate.py downgrade

# Rollback to specific version
python migrate.py downgrade 001
```

### Check Status

```bash
# Show current version
python migrate.py current

# Show migration history
python migrate.py history
```

## Database Compatibility

### PostgreSQL (Production)
- Uses native `UUID` type
- Uses `NOW()` for timestamps
- Supports JSON columns natively

### SQLite (Development)
- Uses `String(36)` for UUIDs
- Uses `CURRENT_TIMESTAMP` for timestamps
- Uses `Text` for JSON (stored as text)

The migrations automatically detect the database type and use appropriate column types.

## Backup and Recovery

### SQLite (Development)
```bash
# Backup
cp iops.db iops.db.backup

# Restore
cp iops.db.backup iops.db
```

### PostgreSQL (Production)
```bash
# Backup
pg_dump -U username -d database_name > backup.sql

# Restore
psql -U username -d database_name < backup.sql
```

## Performance Considerations

### Indexes
All frequently queried columns have indexes:
- Foreign keys (user_id, dataset_id, etc.)
- Lookup fields (email, tier, status)
- Timestamp fields (created_at)
- Composite indexes for common queries

### Query Optimization
- Use `SELECT` with specific columns instead of `SELECT *`
- Use pagination for large result sets
- Use database connection pooling
- Cache expensive queries (5-minute TTL)

## Security

### Data Protection
- Passwords are hashed with bcrypt (10+ rounds)
- Sensitive credentials encrypted with AES-256
- All queries use parameterized statements (SQL injection prevention)

### Access Control
- Foreign key constraints enforce data ownership
- CASCADE DELETE ensures data cleanup
- SET NULL prevents orphaned references

## Monitoring

### Key Metrics
- Table sizes and growth rates
- Query performance (slow query log)
- Index usage statistics
- Connection pool utilization

### Maintenance
- Regular VACUUM (PostgreSQL)
- Index rebuilding if needed
- Database statistics updates
- Backup verification

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
