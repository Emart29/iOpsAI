"""Initial core tables for Phase 1

Revision ID: 001
Revises: 
Create Date: 2024-12-25 00:00:00.000000

This migration creates the core tables needed for Phase 1:
- users: User accounts with tier management
- usage_tracking: Monthly usage tracking per user
- datasets: Uploaded datasets
- analyses: Data analysis workflows

Requirements: 1.1, 1.2
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def get_uuid_column():
    """Return appropriate UUID column type based on database."""
    # For PostgreSQL, use native UUID type
    # For SQLite, use String(36)
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        return postgresql.UUID(as_uuid=True)
    else:
        return sa.String(36)


def upgrade() -> None:
    """Create core tables with indexes and foreign key constraints."""
    
    uuid_type = get_uuid_column()
    bind = op.get_bind()
    
    # Determine appropriate server default for timestamps
    if bind.dialect.name == 'postgresql':
        timestamp_default = sa.text('NOW()')
    else:
        timestamp_default = sa.text('CURRENT_TIMESTAMP')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', uuid_type, primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('tier', sa.String(50), nullable=False, default='free', server_default='free'),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
    )
    
    # Create indexes on users table
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_tier', 'users', ['tier'])
    op.create_index('idx_users_stripe_customer_id', 'users', ['stripe_customer_id'])
    
    # Create usage_tracking table
    op.create_table(
        'usage_tracking',
        sa.Column('id', uuid_type, primary_key=True),
        sa.Column('user_id', uuid_type, nullable=False),
        sa.Column('month_year', sa.String(7), nullable=False),  # Format: '2024-12'
        sa.Column('datasets_count', sa.Integer(), nullable=False, default=0, server_default='0'),
        sa.Column('ai_messages_count', sa.Integer(), nullable=False, default=0, server_default='0'),
        sa.Column('reports_count', sa.Integer(), nullable=False, default=0, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'month_year', name='uq_usage_user_month'),
    )
    
    # Create indexes on usage_tracking table
    op.create_index('idx_usage_tracking_user_id', 'usage_tracking', ['user_id'])
    op.create_index('idx_usage_tracking_user_month', 'usage_tracking', ['user_id', 'month_year'])
    op.create_index('idx_usage_tracking_month_year', 'usage_tracking', ['month_year'])
    
    # Create datasets table
    op.create_table(
        'datasets',
        sa.Column('id', uuid_type, primary_key=True),
        sa.Column('user_id', uuid_type, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('connection_id', uuid_type, nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('column_count', sa.Integer(), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes on datasets table
    op.create_index('idx_datasets_user_id', 'datasets', ['user_id'])
    op.create_index('idx_datasets_connection_id', 'datasets', ['connection_id'])
    op.create_index('idx_datasets_created_at', 'datasets', ['created_at'])
    
    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', uuid_type, primary_key=True),
        sa.Column('user_id', uuid_type, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('dataset_id', uuid_type, nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='draft', server_default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='SET NULL'),
    )
    
    # Create indexes on analyses table
    op.create_index('idx_analyses_user_id', 'analyses', ['user_id'])
    op.create_index('idx_analyses_dataset_id', 'analyses', ['dataset_id'])
    op.create_index('idx_analyses_status', 'analyses', ['status'])
    op.create_index('idx_analyses_created_at', 'analyses', ['created_at'])


def downgrade() -> None:
    """Drop all core tables."""
    
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_table('analyses')
    op.drop_table('datasets')
    op.drop_table('usage_tracking')
    op.drop_table('users')
