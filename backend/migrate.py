"""Database migration runner script.

This script provides a simple interface to run Alembic migrations.
Usage:
    python migrate.py upgrade    # Apply all pending migrations
    python migrate.py downgrade  # Rollback one migration
    python migrate.py current    # Show current migration version
    python migrate.py history    # Show migration history
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alembic.config import Config
from alembic import command


def get_alembic_config():
    """Get Alembic configuration."""
    # Get the directory where this script is located
    base_dir = Path(__file__).parent
    alembic_ini = base_dir / "alembic.ini"
    
    if not alembic_ini.exists():
        raise FileNotFoundError(f"alembic.ini not found at {alembic_ini}")
    
    config = Config(str(alembic_ini))
    return config


def upgrade(revision='head'):
    """Upgrade database to a later version."""
    config = get_alembic_config()
    command.upgrade(config, revision)
    print(f"✅ Database upgraded to {revision}")


def downgrade(revision='-1'):
    """Revert database to a previous version."""
    config = get_alembic_config()
    command.downgrade(config, revision)
    print(f"✅ Database downgraded to {revision}")


def current():
    """Show current migration version."""
    config = get_alembic_config()
    command.current(config)


def history():
    """Show migration history."""
    config = get_alembic_config()
    command.history(config)


def stamp(revision='head'):
    """Mark database as being at a specific revision without running migrations."""
    config = get_alembic_config()
    command.stamp(config, revision)
    print(f"✅ Database stamped at {revision}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [upgrade|downgrade|current|history|stamp]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    try:
        if action == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            upgrade(revision)
        elif action == "downgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else '-1'
            downgrade(revision)
        elif action == "current":
            current()
        elif action == "history":
            history()
        elif action == "stamp":
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            stamp(revision)
        else:
            print(f"Unknown action: {action}")
            print("Available actions: upgrade, downgrade, current, history, stamp")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
