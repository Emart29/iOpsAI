# Database Migration Quick Start Guide

## For New Developers

If you're setting up the project for the first time, follow these steps:

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database

Edit `.env` file:

```bash
# For development (SQLite)
DATABASE_URL=sqlite:///./iops.db

# For production (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
```

### 3. Run Migrations

```bash
# Apply all migrations to create tables
python migrate.py upgrade
```

That's it! Your database is now set up with all core tables.

## For Existing Installations

If you have an existing database with data:

### Option 1: Fresh Start (No Data to Keep)

```bash
# Delete old database
rm iops.db  # or drop PostgreSQL database

# Run migrations
python migrate.py upgrade
```

### Option 2: Migrate Existing Data

```bash
# This will add new columns and tables while preserving existing data
python init_migrations.py
```

## Common Commands

### Check Migration Status

```bash
# Show current migration version
python migrate.py current

# Show all migrations
python migrate.py history
```

### Apply Migrations

```bash
# Apply all pending migrations
python migrate.py upgrade

# Apply up to specific migration
python migrate.py upgrade 001
```

### Rollback Migrations

```bash
# Rollback one migration
python migrate.py downgrade

# Rollback to specific version
python migrate.py downgrade 001
```

## Troubleshooting

### "Table already exists" Error

If you get this error, it means tables were created using the old `init_db()` method:

```bash
# Mark database as up-to-date without running migrations
python migrate.py stamp head
```

### Check What Will Be Created

```bash
# View the migration file
cat migrations/versions/001_initial_core_tables.py
```

### Reset Database (Development Only)

```bash
# Delete database
rm iops.db

# Recreate from scratch
python migrate.py upgrade
```

## What Gets Created

The initial migration creates these tables:

1. **users** - User accounts with tier management
   - Stores email, password, subscription tier
   - Indexes on email, tier, stripe_customer_id

2. **usage_tracking** - Monthly usage tracking
   - Tracks datasets, AI messages, reports per month
   - Enforces tier limits

3. **datasets** - Uploaded datasets
   - Stores file metadata and location
   - Links to users and data connections

4. **analyses** - Analysis workflows
   - Stores analysis configuration and results
   - Links to users and datasets

All tables include:
- Proper foreign key constraints
- Cascade deletes for data cleanup
- Indexes on frequently queried fields
- Timestamps (created_at, updated_at)

## Next Steps

After running migrations:

1. Start the backend server:
   ```bash
   python main.py
   ```

2. The API will be available at `http://localhost:8000`

3. Check the database:
   ```bash
   # For SQLite
   sqlite3 iops.db ".tables"
   
   # For PostgreSQL
   psql -d database_name -c "\dt"
   ```

## Need Help?

- Read `DATABASE_SCHEMA.md` for detailed schema documentation
- Read `migrations/README.md` for migration best practices
- Check migration files in `migrations/versions/` for details

## Important Notes

⚠️ **Never modify existing migrations that have been applied to production**

✅ **Always backup production database before running migrations**

✅ **Test migrations on development database first**

✅ **Review auto-generated migrations before applying**
