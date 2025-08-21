"""Add user models migration

Revision ID: 002
Revises: 001
Create Date: 2025-01-27 11:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types first
    op.execute("CREATE TYPE user_role_enum AS ENUM ('admin', 'analyst', 'viewer', 'developer')")
    op.execute("CREATE TYPE user_status_enum AS ENUM ('active', 'inactive', 'suspended', 'pending_verification')")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'analyst', 'viewer', 'developer', name='user_role_enum'), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', 'pending_verification', name='user_status_enum'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('email_verification_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires', sa.TIMESTAMP(), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(), nullable=True),
        sa.Column('login_attempts', sa.Integer(), nullable=True),
        sa.Column('locked_until', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token'),
        sa.UniqueConstraint('refresh_token'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create user_activities table
    op.create_table('user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('activity_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create indexes
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_status', 'users', ['status'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_session_token', 'user_sessions', ['session_token'])
    op.create_index('idx_user_sessions_refresh_token', 'user_sessions', ['refresh_token'])
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    
    op.create_index('idx_user_activities_user_id', 'user_activities', ['user_id'])
    op.create_index('idx_user_activities_activity_type', 'user_activities', ['activity_type'])
    op.create_index('idx_user_activities_created_at', 'user_activities', ['created_at'])
    
    # Update api_usage table to reference users
    op.add_column('api_usage', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_api_usage_user_id', 'api_usage', 'users', ['user_id'], ['id'])
    op.create_index('idx_api_usage_user_id', 'api_usage', ['user_id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_api_usage_user_id', 'api_usage', type_='foreignkey')
    
    # Drop columns
    op.drop_column('api_usage', 'user_id')
    
    # Drop indexes
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_status', table_name='users')
    op.drop_index('idx_users_created_at', table_name='users')
    
    op.drop_index('idx_user_sessions_user_id', table_name='user_sessions')
    op.drop_index('idx_user_sessions_session_token', table_name='user_sessions')
    op.drop_index('idx_user_sessions_refresh_token', table_name='user_sessions')
    op.drop_index('idx_user_sessions_expires_at', table_name='user_sessions')
    
    op.drop_index('idx_user_activities_user_id', table_name='user_activities')
    op.drop_index('idx_user_activities_activity_type', table_name='user_activities')
    op.drop_index('idx_user_activities_created_at', table_name='user_activities')
    
    # Drop tables
    op.drop_table('user_activities')
    op.drop_index('idx_user_sessions_user_id', table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE user_status_enum")
    op.execute("DROP TYPE user_role_enum")
