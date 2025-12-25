"""Tests for database migrations.

This test suite verifies that migrations create the correct schema.
Note: These tests run migrations directly using Alembic's offline mode
to avoid conflicts with model imports that may auto-create tables.
"""
import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    db_url = f"sqlite:///{db_path}"
    
    yield db_url, db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def alembic_config(temp_db):
    """Create Alembic config for testing with isolated database."""
    db_url, db_path = temp_db
    base_dir = Path(__file__).parent.parent
    alembic_ini = base_dir / "alembic.ini"
    
    config = Config(str(alembic_ini))
    config.set_main_option('sqlalchemy.url', db_url)
    
    # Create a fresh engine for this test
    engine = create_engine(db_url)
    
    return config, engine, db_url


def run_migration_001(engine):
    """Run migration 001 directly without going through env.py."""
    from migrations.versions import _001_initial_core_tables as migration_001
    
    with engine.connect() as connection:
        # Create migration context
        context = MigrationContext.configure(connection)
        op = Operations(context)
        
        # Run the upgrade function directly
        with context.begin_transaction():
            migration_001.upgrade()


def test_migration_001_creates_tables(alembic_config):
    """Test that migration 001 creates all required tables."""
    config, engine, db_url = alembic_config
    
    # Run migration using Alembic command
    command.upgrade(config, "001")
    
    # Connect to database and inspect
    inspector = inspect(engine)
    
    # Check that all tables were created
    tables = inspector.get_table_names()
    assert 'users' in tables, "users table not created"
    assert 'usage_tracking' in tables, "usage_tracking table not created"
    assert 'datasets' in tables, "datasets table not created"
    assert 'analyses' in tables, "analyses table not created"
    
    engine.dispose()


def test_migration_001_creates_indexes(alembic_config):
    """Test that migration 001 creates all required indexes."""
    config, engine, db_url = alembic_config
    
    # Run migration
    command.upgrade(config, "001")
    
    # Connect to database and inspect
    inspector = inspect(engine)
    
    # Check users table indexes
    users_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    assert 'idx_users_email' in users_indexes
    assert 'idx_users_tier' in users_indexes
    assert 'idx_users_stripe_customer_id' in users_indexes
    
    # Check usage_tracking table indexes
    usage_indexes = [idx['name'] for idx in inspector.get_indexes('usage_tracking')]
    assert 'idx_usage_tracking_user_id' in usage_indexes
    assert 'idx_usage_tracking_user_month' in usage_indexes
    assert 'idx_usage_tracking_month_year' in usage_indexes
    
    # Check datasets table indexes
    datasets_indexes = [idx['name'] for idx in inspector.get_indexes('datasets')]
    assert 'idx_datasets_user_id' in datasets_indexes
    assert 'idx_datasets_connection_id' in datasets_indexes
    assert 'idx_datasets_created_at' in datasets_indexes
    
    # Check analyses table indexes
    analyses_indexes = [idx['name'] for idx in inspector.get_indexes('analyses')]
    assert 'idx_analyses_user_id' in analyses_indexes
    assert 'idx_analyses_dataset_id' in analyses_indexes
    assert 'idx_analyses_status' in analyses_indexes
    assert 'idx_analyses_created_at' in analyses_indexes
    
    engine.dispose()


def test_migration_001_creates_foreign_keys(alembic_config):
    """Test that migration 001 creates foreign key constraints."""
    config, engine, db_url = alembic_config
    
    # Run migration
    command.upgrade(config, "001")
    
    # Connect to database and inspect
    inspector = inspect(engine)
    
    # Check usage_tracking foreign keys
    usage_fks = inspector.get_foreign_keys('usage_tracking')
    assert len(usage_fks) > 0, "usage_tracking should have foreign keys"
    assert any(fk['referred_table'] == 'users' for fk in usage_fks)
    
    # Check datasets foreign keys
    datasets_fks = inspector.get_foreign_keys('datasets')
    assert len(datasets_fks) > 0, "datasets should have foreign keys"
    assert any(fk['referred_table'] == 'users' for fk in datasets_fks)
    
    # Check analyses foreign keys
    analyses_fks = inspector.get_foreign_keys('analyses')
    assert len(analyses_fks) > 0, "analyses should have foreign keys"
    assert any(fk['referred_table'] == 'users' for fk in analyses_fks)
    assert any(fk['referred_table'] == 'datasets' for fk in analyses_fks)
    
    engine.dispose()


def test_migration_001_users_table_columns(alembic_config):
    """Test that users table has all required columns."""
    config, engine, db_url = alembic_config
    
    # Run migration
    command.upgrade(config, "001")
    
    # Connect to database and inspect
    inspector = inspect(engine)
    
    columns = {col['name']: col for col in inspector.get_columns('users')}
    
    # Check required columns exist
    required_columns = [
        'id', 'email', 'password_hash', 'full_name', 'tier',
        'stripe_customer_id', 'stripe_subscription_id', 'is_admin',
        'created_at', 'updated_at'
    ]
    
    for col_name in required_columns:
        assert col_name in columns, f"Column {col_name} missing from users table"
    
    # Check column properties
    assert columns['email']['nullable'] == False
    assert columns['password_hash']['nullable'] == False
    assert columns['tier']['nullable'] == False
    assert columns['is_admin']['nullable'] == False
    
    engine.dispose()


def test_migration_001_usage_tracking_table_columns(alembic_config):
    """Test that usage_tracking table has all required columns."""
    config, engine, db_url = alembic_config
    
    # Run migration
    command.upgrade(config, "001")
    
    # Connect to database and inspect
    inspector = inspect(engine)
    
    columns = {col['name']: col for col in inspector.get_columns('usage_tracking')}
    
    # Check required columns exist
    required_columns = [
        'id', 'user_id', 'month_year', 'datasets_count',
        'ai_messages_count', 'reports_count', 'created_at', 'updated_at'
    ]
    
    for col_name in required_columns:
        assert col_name in columns, f"Column {col_name} missing from usage_tracking table"
    
    # Check column properties
    assert columns['user_id']['nullable'] == False
    assert columns['month_year']['nullable'] == False
    
    engine.dispose()


def test_migration_001_downgrade(alembic_config):
    """Test that migration 001 can be rolled back."""
    config, engine, db_url = alembic_config
    
    # Run migration
    command.upgrade(config, "001")
    
    # Verify tables exist
    inspector = inspect(engine)
    tables_before = inspector.get_table_names()
    assert len(tables_before) >= 4
    
    # Rollback migration
    command.downgrade(config, "base")
    
    # Verify tables are removed
    inspector = inspect(engine)
    tables_after = inspector.get_table_names()
    
    # Only alembic_version table should remain
    assert 'users' not in tables_after
    assert 'usage_tracking' not in tables_after
    assert 'datasets' not in tables_after
    assert 'analyses' not in tables_after
    
    engine.dispose()


def test_migration_001_unique_constraints(alembic_config):
    """Test that unique constraints are properly created."""
    config, engine, db_url = alembic_config
    
    # Run migration
    command.upgrade(config, "001")
    
    # Connect to database
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test unique constraint on usage_tracking (user_id, month_year)
    # Insert first record
    session.execute(text("""
        INSERT INTO users (id, email, password_hash, tier, is_admin, created_at, updated_at)
        VALUES ('user-1', 'test@example.com', 'hash', 'free', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """))
    
    session.execute(text("""
        INSERT INTO usage_tracking (id, user_id, month_year, datasets_count, ai_messages_count, reports_count, created_at, updated_at)
        VALUES ('usage-1', 'user-1', '2024-12', 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """))
    session.commit()
    
    # Try to insert duplicate - should fail
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        session.execute(text("""
            INSERT INTO usage_tracking (id, user_id, month_year, datasets_count, ai_messages_count, reports_count, created_at, updated_at)
            VALUES ('usage-2', 'user-1', '2024-12', 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """))
        session.commit()
    
    session.close()
    engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
