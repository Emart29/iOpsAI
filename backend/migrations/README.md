# Database Migrations

This directory contains Alembic database migrations for the iOps application.

## Overview

Migrations are version-controlled changes to the database schema. Each migration file represents a specific change to the database structure.

## Migration Files

- `env.py` - Alembic environment configuration
- `script.py.mako` - Template for generating new migration files
- `versions/` - Directory containing migration scripts

### Current Migrations

1. **001_initial_core_tables.py** - Creates core tables for Phase 1
   - `users` - User accounts with tier management
   - `usage_tracking` - Monthly usage tracking per user
   - `datasets` - Uploaded datasets
   - `analyses` - Data analysis workflows
   - Includes all necessary indexes and foreign key constraints
   - Requirements: 1.1, 1.2

## Running Migrations

### Using the migrate.py script (Recommended)

```bash
# Apply all pending migrations
python migrate.py upgrade

# Rollback one migration
python migrate.py downgrade

# Show current migration version
python migrate.py current

# Show migration history
python migrate.py history

# Mark database at specific version without running migrations
python migrate.py stamp head
```

### Using Alembic directly

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## Creating New Migrations

When you need to add new tables or modify existing ones:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration file
alembic revision -m "description of changes"
```

## Database Support

These migrations support both:
- **PostgreSQL** (production) - Uses native UUID type
- **SQLite** (development) - Uses String(36) for UUIDs

The migrations automatically detect the database type and use appropriate column types.

## Migration Best Practices

1. **Always test migrations** on a development database first
2. **Backup production database** before running migrations
3. **Review auto-generated migrations** - they may need manual adjustments
4. **Never modify existing migrations** that have been applied to production
5. **Use descriptive names** for migration files
6. **Document requirements** in migration docstrings

## Troubleshooting

### Migration fails with "table already exists"

If tables already exist from the old `init_db()` approach:

```bash
# Mark database as being at the latest version without running migrations
python migrate.py stamp head
```

### Reset database (development only)

```bash
# Delete the database file (SQLite)
rm iops.db

# Or drop all tables (PostgreSQL)
# Then run migrations from scratch
python migrate.py upgrade
```

### Check migration status

```bash
python migrate.py current
python migrate.py history
```

## Schema Overview

### users
- Primary key: `id` (UUID)
- Indexes: `email`, `tier`, `stripe_customer_id`
- Tracks user accounts and subscription tiers

### usage_tracking
- Primary key: `id` (UUID)
- Foreign key: `user_id` → `users.id` (CASCADE)
- Unique constraint: `(user_id, month_year)`
- Indexes: `user_id`, `(user_id, month_year)`, `month_year`
- Tracks monthly resource usage per user

### datasets
- Primary key: `id` (UUID)
- Foreign key: `user_id` → `users.id` (CASCADE)
- Indexes: `user_id`, `connection_id`, `created_at`
- Stores uploaded dataset metadata

### analyses
- Primary key: `id` (UUID)
- Foreign keys:
  - `user_id` → `users.id` (CASCADE)
  - `dataset_id` → `datasets.id` (SET NULL)
- Indexes: `user_id`, `dataset_id`, `status`, `created_at`
- Stores analysis workflows and results

## Future Migrations

Additional migrations will be created for:
- Phase 2: Reports table (public sharing)
- Phase 3: Charts and embeds
- Phase 4: Billing and subscriptions
- Phase 5: Templates and marketplace
- Phase 6: Collaboration tables
- Phase 7: Data connections and analytics
