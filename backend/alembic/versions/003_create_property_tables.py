"""Create property data tables

Revision ID: 003
Revises: 002_add_user_models
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_user_models'
branch_labels = None
depends_on = None


def upgrade():
    # Create properties table
    op.create_table('properties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('source_id', sa.String(length=200), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('price_currency', sa.String(length=10), nullable=True),
        sa.Column('location', sa.String(length=300), nullable=False),
        sa.Column('property_type', sa.String(length=100), nullable=False),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('bathrooms', sa.Integer(), nullable=True),
        sa.Column('area_sqft', sa.Float(), nullable=True),
        sa.Column('area_sqm', sa.Float(), nullable=True),
        sa.Column('developer', sa.String(length=200), nullable=True),
        sa.Column('completion_date', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amenities', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('listing_date', sa.String(length=100), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('agent_name', sa.String(length=200), nullable=True),
        sa.Column('agent_phone', sa.String(length=50), nullable=True),
        sa.Column('agent_email', sa.String(length=200), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('crawled_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for properties table
    op.create_index('idx_properties_source', 'properties', ['source'])
    op.create_index('idx_properties_source_id', 'properties', ['source_id'])
    op.create_index('idx_properties_url', 'properties', ['url'])
    op.create_index('idx_properties_price', 'properties', ['price'])
    op.create_index('idx_properties_location', 'properties', ['location'])
    op.create_index('idx_properties_type', 'properties', ['property_type'])
    op.create_index('idx_properties_bedrooms', 'properties', ['bedrooms'])
    op.create_index('idx_properties_bathrooms', 'properties', ['bathrooms'])
    op.create_index('idx_properties_area_sqft', 'properties', ['area_sqft'])
    op.create_index('idx_properties_area_sqm', 'properties', ['area_sqm'])
    op.create_index('idx_properties_developer', 'properties', ['developer'])
    op.create_index('idx_properties_latitude', 'properties', ['latitude'])
    op.create_index('idx_properties_longitude', 'properties', ['longitude'])
    op.create_index('idx_properties_verification_status', 'properties', ['verification_status'])
    op.create_index('idx_properties_data_quality', 'properties', ['data_quality_score'])
    op.create_index('idx_properties_crawled_at', 'properties', ['crawled_at'])
    op.create_index('idx_properties_created_at', 'properties', ['created_at'])
    op.create_index('idx_properties_updated_at', 'properties', ['updated_at'])
    
    # Composite indexes for better query performance
    op.create_index('idx_properties_source_location', 'properties', ['source', 'location'])
    op.create_index('idx_properties_type_price', 'properties', ['property_type', 'price'])
    op.create_index('idx_properties_bedrooms_bathrooms', 'properties', ['bedrooms', 'bathrooms'])
    op.create_index('idx_properties_coordinates', 'properties', ['latitude', 'longitude'])
    
    # Create property_price_history table
    op.create_table('property_price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('price_currency', sa.String(length=10), nullable=True),
        sa.Column('change_date', sa.DateTime(), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=True),
        sa.Column('change_amount', sa.Float(), nullable=True),
        sa.Column('change_percentage', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for property_price_history table
    op.create_index('idx_price_history_property_id', 'property_price_history', ['property_id'])
    op.create_index('idx_price_history_change_date', 'property_price_history', ['change_date'])
    op.create_index('idx_price_history_property_date', 'property_price_history', ['property_id', 'change_date'])
    
    # Create property_similarities table
    op.create_table('property_similarities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('similar_property_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('similarity_factors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for property_similarities table
    op.create_index('idx_similarities_property_id', 'property_similarities', ['property_id'])
    op.create_index('idx_similarities_similar_property_id', 'property_similarities', ['similar_property_id'])
    op.create_index('idx_similarities_score', 'property_similarities', ['similarity_score'])
    
    # Create crawl_sessions table
    op.create_table('crawl_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('session_start', sa.DateTime(), nullable=False),
        sa.Column('session_end', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('pages_crawled', sa.Integer(), nullable=True),
        sa.Column('properties_found', sa.Integer(), nullable=True),
        sa.Column('properties_parsed', sa.Integer(), nullable=True),
        sa.Column('errors_encountered', sa.Integer(), nullable=True),
        sa.Column('max_pages', sa.Integer(), nullable=True),
        sa.Column('request_delay', sa.Float(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for crawl_sessions table
    op.create_index('idx_crawl_sessions_source', 'crawl_sessions', ['source'])
    op.create_index('idx_crawl_sessions_status', 'crawl_sessions', ['status'])
    op.create_index('idx_crawl_sessions_source_status', 'crawl_sessions', ['source', 'status'])
    op.create_index('idx_crawl_sessions_session_start', 'crawl_sessions', ['session_start'])
    
    # Create data_quality_metrics table
    op.create_table('data_quality_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('crawl_date', sa.DateTime(), nullable=False),
        sa.Column('total_properties', sa.Integer(), nullable=True),
        sa.Column('properties_with_price', sa.Integer(), nullable=True),
        sa.Column('properties_with_location', sa.Integer(), nullable=True),
        sa.Column('properties_with_coordinates', sa.Integer(), nullable=True),
        sa.Column('properties_with_images', sa.Integer(), nullable=True),
        sa.Column('properties_with_amenities', sa.Integer(), nullable=True),
        sa.Column('avg_data_quality_score', sa.Float(), nullable=True),
        sa.Column('avg_price_completeness', sa.Float(), nullable=True),
        sa.Column('avg_location_completeness', sa.Float(), nullable=True),
        sa.Column('newest_listing_date', sa.DateTime(), nullable=True),
        sa.Column('oldest_listing_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for data_quality_metrics table
    op.create_index('idx_data_quality_source', 'data_quality_metrics', ['source'])
    op.create_index('idx_data_quality_crawl_date', 'data_quality_metrics', ['crawl_date'])
    op.create_index('idx_data_quality_source_date', 'data_quality_metrics', ['source', 'crawl_date'])
    
    # Create market_trends table
    op.create_table('market_trends',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_date', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(length=300), nullable=False),
        sa.Column('property_type', sa.String(length=100), nullable=False),
        sa.Column('avg_price', sa.Float(), nullable=True),
        sa.Column('median_price', sa.Float(), nullable=True),
        sa.Column('min_price', sa.Float(), nullable=True),
        sa.Column('max_price', sa.Float(), nullable=True),
        sa.Column('price_per_sqft', sa.Float(), nullable=True),
        sa.Column('total_listings', sa.Integer(), nullable=True),
        sa.Column('new_listings', sa.Integer(), nullable=True),
        sa.Column('price_changes', sa.Integer(), nullable=True),
        sa.Column('avg_days_on_market', sa.Float(), nullable=True),
        sa.Column('market_activity_score', sa.Float(), nullable=True),
        sa.Column('price_volatility', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for market_trends table
    op.create_index('idx_market_trends_location', 'market_trends', ['location'])
    op.create_index('idx_market_trends_property_type', 'market_trends', ['property_type'])
    op.create_index('idx_market_trends_location_type', 'market_trends', ['location', 'property_type'])
    op.create_index('idx_market_trends_analysis_date', 'market_trends', ['analysis_date'])
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_price_history_property_id', 
        'property_price_history', 
        'properties', 
        ['property_id'], 
        ['id']
    )
    
    op.create_foreign_key(
        'fk_similarities_property_id', 
        'property_similarities', 
        'properties', 
        ['property_id'], 
        ['id']
    )
    
    op.create_foreign_key(
        'fk_similarities_similar_property_id', 
        'property_similarities', 
        'properties', 
        ['similar_property_id'], 
        ['id']
    )


def downgrade():
    # Drop foreign key constraints first
    op.drop_constraint('fk_similarities_similar_property_id', 'property_similarities', type_='foreignkey')
    op.drop_constraint('fk_similarities_property_id', 'property_similarities', type_='foreignkey')
    op.drop_constraint('fk_price_history_property_id', 'property_price_history', type_='foreignkey')
    
    # Drop tables in reverse order
    op.drop_table('market_trends')
    op.drop_table('data_quality_metrics')
    op.drop_table('crawl_sessions')
    op.drop_table('property_similarities')
    op.drop_table('property_price_history')
    op.drop_table('properties')
