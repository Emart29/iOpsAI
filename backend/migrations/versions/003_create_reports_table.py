"""Create reports table for public report sharing

Revision ID: 003
Revises: 002
Create Date: 2024-12-25

This migration creates the reports table for Phase 2:
- reports: Public shareable reports with short codes

Requirements: 2.1, 2.2
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def get_uuid_column():
    """Return appropriate UUID column type based on database."""
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        return postgresql.UUID(as_uuid=True)
    else:
        return sa.String(36)


def upgrade() -> None:
    """Create reports table with indexes and foreign key constraints."""
    
    uuid_type = get_uuid_column()
    bind = op.get_bind()
    
    # Determine appropriate server default for timestamps
    if bind.dialect.name == 'postgresql':
        timestamp_default = sa.text('NOW()')
    else:
        timestamp_default = sa.text('CURRENT_TIMESTAMP')
    
    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', uuid_type, primary_key=True),
        sa.Column('analysis_id', uuid_type, nullable=False),
        sa.Column('short_code', sa.String(20), nullable=False, unique=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True, server_default='1'),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=timestamp_default),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )
    
    # Create unique index on short_code for fast lookups
    op.create_index('idx_reports_short_code', 'reports', ['short_code'], unique=True)
    
    # Create index on analysis_id for foreign key lookups
    op.create_index('idx_reports_analysis_id', 'reports', ['analysis_id'])
    
    # Create index on expires_at for filtering expired reports
    op.create_index('idx_reports_expires_at', 'reports', ['expires_at'])


def downgrade() -> None:
    """Drop reports table."""
    op.drop_table('reports')
