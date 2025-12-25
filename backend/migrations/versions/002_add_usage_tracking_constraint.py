"""add usage tracking unique constraint

Revision ID: 002
Revises: 001
Create Date: 2024-12-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraint to usage_tracking table."""
    # Add unique constraint on user_id and month_year
    op.create_unique_constraint(
        'uq_user_month',
        'usage_tracking',
        ['user_id', 'month_year']
    )
    
    # Update tier column to use enum (if using PostgreSQL)
    # For SQLite, this will be a no-op as it doesn't support enum natively
    try:
        op.alter_column('users', 'tier',
                       existing_type=sa.String(50),
                       type_=sa.Enum('free', 'pro', 'team', 'enterprise', name='usertier'),
                       existing_nullable=False,
                       existing_server_default='free')
    except Exception:
        # SQLite doesn't support ALTER COLUMN, so we skip this
        pass


def downgrade():
    """Remove unique constraint from usage_tracking table."""
    op.drop_constraint('uq_user_month', 'usage_tracking', type_='unique')
    
    # Revert tier column to string (if using PostgreSQL)
    try:
        op.alter_column('users', 'tier',
                       existing_type=sa.Enum('free', 'pro', 'team', 'enterprise', name='usertier'),
                       type_=sa.String(50),
                       existing_nullable=False,
                       existing_server_default='free')
    except Exception:
        pass
