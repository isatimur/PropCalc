"""Enhanced data sources migration

Revision ID: 001
Revises:
Create Date: 2025-01-27 10:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create developers table
    op.create_table('developers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.String(length=50), nullable=False),
        sa.Column('developer_number', sa.String(length=50), nullable=True),
        sa.Column('developer_name_ar', sa.String(length=255), nullable=True),
        sa.Column('developer_name_en', sa.String(length=255), nullable=True),
        sa.Column('developer_type', sa.String(length=100), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('contact_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('developer_id')
    )

    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=50), nullable=False),
        sa.Column('project_number', sa.String(length=50), nullable=True),
        sa.Column('project_name_ar', sa.String(length=255), nullable=True),
        sa.Column('project_name_en', sa.String(length=255), nullable=True),
        sa.Column('developer_id', sa.String(length=50), nullable=True),
        sa.Column('developer_name', sa.String(length=255), nullable=True),
        sa.Column('master_developer_id', sa.String(length=50), nullable=True),
        sa.Column('master_developer_name', sa.String(length=255), nullable=True),
        sa.Column('project_start_date', sa.Date(), nullable=True),
        sa.Column('project_end_date', sa.Date(), nullable=True),
        sa.Column('project_type_id', sa.Integer(), nullable=True),
        sa.Column('project_type_ar', sa.String(length=100), nullable=True),
        sa.Column('project_type_en', sa.String(length=100), nullable=True),
        sa.Column('project_classification_id', sa.Integer(), nullable=True),
        sa.Column('project_classification_ar', sa.String(length=100), nullable=True),
        sa.Column('project_classification_en', sa.String(length=100), nullable=True),
        sa.Column('escrow_agent_id', sa.String(length=50), nullable=True),
        sa.Column('escrow_agent_name', sa.String(length=255), nullable=True),
        sa.Column('project_status', sa.String(length=50), nullable=True),
        sa.Column('project_status_ar', sa.String(length=100), nullable=True),
        sa.Column('project_status_en', sa.String(length=100), nullable=True),
        sa.Column('percent_completed', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('cancellation_date', sa.Date(), nullable=True),
        sa.Column('project_description_ar', sa.Text(), nullable=True),
        sa.Column('project_description_en', sa.Text(), nullable=True),
        sa.Column('property_id', sa.String(length=50), nullable=True),
        sa.Column('area_id', sa.Integer(), nullable=True),
        sa.Column('area_name_ar', sa.String(length=255), nullable=True),
        sa.Column('area_name_en', sa.String(length=255), nullable=True),
        sa.Column('master_project_ar', sa.String(length=255), nullable=True),
        sa.Column('master_project_en', sa.String(length=255), nullable=True),
        sa.Column('zoning_authority_id', sa.Integer(), nullable=True),
        sa.Column('zoning_authority_ar', sa.String(length=100), nullable=True),
        sa.Column('zoning_authority_en', sa.String(length=100), nullable=True),
        sa.Column('no_of_lands', sa.Integer(), nullable=True),
        sa.Column('no_of_buildings', sa.Integer(), nullable=True),
        sa.Column('no_of_villas', sa.Integer(), nullable=True),
        sa.Column('no_of_units', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id')
    )

    # Create buildings table
    op.create_table('buildings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.String(length=50), nullable=False),
        sa.Column('area_id', sa.Integer(), nullable=True),
        sa.Column('zone_id', sa.Integer(), nullable=True),
        sa.Column('area_name_ar', sa.String(length=255), nullable=True),
        sa.Column('area_name_en', sa.String(length=255), nullable=True),
        sa.Column('land_number', sa.String(length=50), nullable=True),
        sa.Column('land_sub_number', sa.String(length=50), nullable=True),
        sa.Column('building_number', sa.String(length=50), nullable=True),
        sa.Column('common_area', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('actual_common_area', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('floors', sa.Integer(), nullable=True),
        sa.Column('rooms', sa.String(length=50), nullable=True),
        sa.Column('rooms_ar', sa.String(length=100), nullable=True),
        sa.Column('rooms_en', sa.String(length=100), nullable=True),
        sa.Column('car_parks', sa.Integer(), nullable=True),
        sa.Column('built_up_area', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('bld_levels', sa.Integer(), nullable=True),
        sa.Column('shops', sa.Integer(), nullable=True),
        sa.Column('flats', sa.Integer(), nullable=True),
        sa.Column('offices', sa.Integer(), nullable=True),
        sa.Column('swimming_pools', sa.Integer(), nullable=True),
        sa.Column('elevators', sa.Integer(), nullable=True),
        sa.Column('actual_area', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('property_type_id', sa.Integer(), nullable=True),
        sa.Column('property_type_ar', sa.String(length=100), nullable=True),
        sa.Column('property_type_en', sa.String(length=100), nullable=True),
        sa.Column('property_sub_type_id', sa.Integer(), nullable=True),
        sa.Column('property_sub_type_ar', sa.String(length=100), nullable=True),
        sa.Column('property_sub_type_en', sa.String(length=100), nullable=True),
        sa.Column('parent_property_id', sa.String(length=50), nullable=True),
        sa.Column('creation_date', sa.Date(), nullable=True),
        sa.Column('parcel_id', sa.String(length=50), nullable=True),
        sa.Column('is_free_hold', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('is_lease_hold', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('is_registered', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('pre_registration_number', sa.String(length=50), nullable=True),
        sa.Column('master_project_id', sa.String(length=50), nullable=True),
        sa.Column('master_project_en', sa.String(length=255), nullable=True),
        sa.Column('master_project_ar', sa.String(length=255), nullable=True),
        sa.Column('project_id', sa.String(length=50), nullable=True),
        sa.Column('project_name_ar', sa.String(length=255), nullable=True),
        sa.Column('project_name_en', sa.String(length=255), nullable=True),
        sa.Column('land_type_id', sa.Integer(), nullable=True),
        sa.Column('land_type_ar', sa.String(length=100), nullable=True),
        sa.Column('land_type_en', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('property_id')
    )

    # Create units table
    op.create_table('units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.String(length=50), nullable=True),
        sa.Column('area_id', sa.Integer(), nullable=True),
        sa.Column('zone_id', sa.Integer(), nullable=True),
        sa.Column('area_name_ar', sa.String(length=255), nullable=True),
        sa.Column('area_name_en', sa.String(length=255), nullable=True),
        sa.Column('land_number', sa.String(length=50), nullable=True),
        sa.Column('building_number', sa.String(length=50), nullable=True),
        sa.Column('unit_number', sa.String(length=50), nullable=True),
        sa.Column('unit_balcony_area', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('unit_parking_number', sa.String(length=50), nullable=True),
        sa.Column('floor', sa.String(length=20), nullable=True),
        sa.Column('rooms', sa.String(length=50), nullable=True),
        sa.Column('actual_area', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('property_type_id', sa.Integer(), nullable=True),
        sa.Column('property_type_ar', sa.String(length=100), nullable=True),
        sa.Column('property_type_en', sa.String(length=100), nullable=True),
        sa.Column('property_sub_type_id', sa.Integer(), nullable=True),
        sa.Column('property_sub_type_ar', sa.String(length=100), nullable=True),
        sa.Column('property_sub_type_en', sa.String(length=100), nullable=True),
        sa.Column('master_project_id', sa.String(length=50), nullable=True),
        sa.Column('master_project_en', sa.String(length=255), nullable=True),
        sa.Column('project_id', sa.String(length=50), nullable=True),
        sa.Column('project_name_en', sa.String(length=255), nullable=True),
        sa.Column('land_type_id', sa.Integer(), nullable=True),
        sa.Column('land_type_en', sa.String(length=100), nullable=True),
        sa.Column('creation_date', sa.Date(), nullable=True),
        sa.Column('is_free_hold', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('is_lease_hold', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('is_registered', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create brokers table
    op.create_table('brokers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=50), nullable=False),
        sa.Column('real_estate_broker_id', sa.String(length=50), nullable=True),
        sa.Column('broker_number', sa.String(length=50), nullable=True),
        sa.Column('broker_name_ar', sa.String(length=255), nullable=True),
        sa.Column('broker_name_en', sa.String(length=255), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('license_start_date', sa.Date(), nullable=True),
        sa.Column('license_end_date', sa.Date(), nullable=True),
        sa.Column('webpage', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('fax', sa.String(length=50), nullable=True),
        sa.Column('real_estate_id', sa.String(length=50), nullable=True),
        sa.Column('real_estate_number', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('participant_id'),
        sa.UniqueConstraint('broker_number')
    )

    # Create offices table
    op.create_table('offices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=50), nullable=True),
        sa.Column('real_estate_id', sa.String(length=50), nullable=False),
        sa.Column('real_estate_number', sa.String(length=50), nullable=True),
        sa.Column('license_source_id', sa.Integer(), nullable=True),
        sa.Column('license_source_ar', sa.String(length=100), nullable=True),
        sa.Column('license_source_en', sa.String(length=100), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('is_branch', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('main_office_id', sa.String(length=50), nullable=True),
        sa.Column('webpage', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('fax', sa.String(length=50), nullable=True),
        sa.Column('activity_type_id', sa.Integer(), nullable=True),
        sa.Column('ded_activity_code', sa.String(length=20), nullable=True),
        sa.Column('activity_type_ar', sa.String(length=100), nullable=True),
        sa.Column('activity_type_en', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('real_estate_id')
    )

    # Create valuators table
    op.create_table('valuators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('valuation_company_number', sa.String(length=50), nullable=True),
        sa.Column('valuation_company_name_ar', sa.String(length=255), nullable=True),
        sa.Column('valuation_company_name_en', sa.String(length=255), nullable=True),
        sa.Column('valuator_number', sa.String(length=50), nullable=True),
        sa.Column('valuator_name_ar', sa.String(length=255), nullable=True),
        sa.Column('valuator_name_en', sa.String(length=255), nullable=True),
        sa.Column('valuator_nationality_id', sa.Integer(), nullable=True),
        sa.Column('valuator_nationality_en', sa.String(length=100), nullable=True),
        sa.Column('gender_id', sa.Integer(), nullable=True),
        sa.Column('gender_en', sa.String(length=20), nullable=True),
        sa.Column('license_start_date', sa.Date(), nullable=True),
        sa.Column('license_end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('valuator_number')
    )

    # Create permits table
    op.create_table('permits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('permits_id', sa.String(length=50), nullable=False),
        sa.Column('permit_number', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('location', sa.Text(), nullable=True),
        sa.Column('exhibition_name_ar', sa.String(length=255), nullable=True),
        sa.Column('exhibition_name_en', sa.String(length=255), nullable=True),
        sa.Column('permit_status_id', sa.Integer(), nullable=True),
        sa.Column('permit_status_en', sa.String(length=100), nullable=True),
        sa.Column('parent_service_id', sa.Integer(), nullable=True),
        sa.Column('main_service_en', sa.String(length=255), nullable=True),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('service_ar', sa.String(length=100), nullable=True),
        sa.Column('service_en', sa.String(length=100), nullable=True),
        sa.Column('sub_service_id', sa.Integer(), nullable=True),
        sa.Column('sub_service_ar', sa.String(length=100), nullable=True),
        sa.Column('sub_service_en', sa.String(length=100), nullable=True),
        sa.Column('applicant_id', sa.String(length=50), nullable=True),
        sa.Column('applicant_name_ar', sa.String(length=255), nullable=True),
        sa.Column('applicant_name_en', sa.String(length=255), nullable=True),
        sa.Column('applicant_type_id', sa.Integer(), nullable=True),
        sa.Column('applicant_type_ar', sa.String(length=100), nullable=True),
        sa.Column('applicant_type_en', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('permits_id')
    )

    # Create map_requests table
    op.create_table('map_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(length=50), nullable=False),
        sa.Column('request_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('application_ar', sa.String(length=100), nullable=True),
        sa.Column('sub_service_application_en', sa.String(length=100), nullable=True),
        sa.Column('request_source_id', sa.Integer(), nullable=True),
        sa.Column('request_source_ar', sa.String(length=100), nullable=True),
        sa.Column('request_source_en', sa.String(length=100), nullable=True),
        sa.Column('procedure_id', sa.Integer(), nullable=True),
        sa.Column('procedure_name_ar', sa.String(length=100), nullable=True),
        sa.Column('procedure_name_en', sa.String(length=100), nullable=True),
        sa.Column('property_type_id', sa.Integer(), nullable=True),
        sa.Column('property_type_ar', sa.String(length=100), nullable=True),
        sa.Column('property_type_en', sa.String(length=100), nullable=True),
        sa.Column('no_of_siteplans', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )

    # Create rent_contracts table
    op.create_table('rent_contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.String(length=50), nullable=False),
        sa.Column('contract_number', sa.String(length=50), nullable=True),
        sa.Column('contract_date', sa.Date(), nullable=True),
        sa.Column('contract_type', sa.String(length=100), nullable=True),
        sa.Column('property_id', sa.String(length=50), nullable=True),
        sa.Column('unit_id', sa.String(length=50), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('tenant_name_ar', sa.String(length=255), nullable=True),
        sa.Column('tenant_name_en', sa.String(length=255), nullable=True),
        sa.Column('landlord_id', sa.String(length=50), nullable=True),
        sa.Column('landlord_name_ar', sa.String(length=255), nullable=True),
        sa.Column('landlord_name_en', sa.String(length=255), nullable=True),
        sa.Column('rent_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('rent_currency', sa.String(length=10), nullable=True),
        sa.Column('contract_start_date', sa.Date(), nullable=True),
        sa.Column('contract_end_date', sa.Date(), nullable=True),
        sa.Column('contract_status', sa.String(length=50), nullable=True),
        sa.Column('area_sqft', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('bathrooms', sa.Integer(), nullable=True),
        sa.Column('parking_spaces', sa.Integer(), nullable=True),
        sa.Column('location_ar', sa.String(length=255), nullable=True),
        sa.Column('location_en', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_id')
    )

    # Create valuations table
    op.create_table('valuations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('valuation_id', sa.String(length=50), nullable=False),
        sa.Column('property_id', sa.String(length=50), nullable=True),
        sa.Column('valuator_id', sa.String(length=50), nullable=True),
        sa.Column('valuation_date', sa.Date(), nullable=True),
        sa.Column('valuation_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('valuation_currency', sa.String(length=10), nullable=True),
        sa.Column('valuation_type', sa.String(length=100), nullable=True),
        sa.Column('valuation_method', sa.String(length=100), nullable=True),
        sa.Column('valuation_status', sa.String(length=50), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('valuation_id')
    )

    # Create additional licensing tables
    op.create_table('free_zone_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.String(length=50), nullable=False),
        sa.Column('company_name_ar', sa.String(length=255), nullable=True),
        sa.Column('company_name_en', sa.String(length=255), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('free_zone_name', sa.String(length=100), nullable=True),
        sa.Column('activity_type', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id')
    )

    op.create_table('licensed_owner_associations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('association_id', sa.String(length=50), nullable=False),
        sa.Column('association_name_ar', sa.String(length=255), nullable=True),
        sa.Column('association_name_en', sa.String(length=255), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('contact_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('association_id')
    )

    op.create_table('real_estate_licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('license_id', sa.String(length=50), nullable=False),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('license_type', sa.String(length=100), nullable=True),
        sa.Column('licensee_name_ar', sa.String(length=255), nullable=True),
        sa.Column('licensee_name_en', sa.String(length=255), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('activity_type', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('contact_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('license_id')
    )

    op.create_table('accredited_escrow_agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(length=50), nullable=False),
        sa.Column('agent_name_ar', sa.String(length=255), nullable=True),
        sa.Column('agent_name_en', sa.String(length=255), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('license_issue_date', sa.Date(), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('contact_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id')
    )

    # Create foreign key constraints
    op.create_foreign_key('fk_projects_developer_id', 'projects', 'developers', ['developer_id'], ['developer_id'])
    op.create_foreign_key('fk_buildings_project_id', 'buildings', 'projects', ['project_id'], ['project_id'])
    op.create_foreign_key('fk_units_property_id', 'units', 'buildings', ['property_id'], ['property_id'])
    op.create_foreign_key('fk_units_project_id', 'units', 'projects', ['project_id'], ['project_id'])
    op.create_foreign_key('fk_offices_participant_id', 'offices', 'brokers', ['participant_id'], ['participant_id'])
    op.create_foreign_key('fk_valuations_property_id', 'valuations', 'buildings', ['property_id'], ['property_id'])
    op.create_foreign_key('fk_valuations_valuator_id', 'valuations', 'valuators', ['valuator_id'], ['valuator_number'])

    # Create indexes
    op.create_index('idx_developers_developer_id', 'developers', ['developer_id'])
    op.create_index('idx_developers_license_expiry', 'developers', ['license_expiry_date'])
    op.create_index('idx_developers_status', 'developers', ['status'])

    op.create_index('idx_projects_project_id', 'projects', ['project_id'])
    op.create_index('idx_projects_developer_id', 'projects', ['developer_id'])
    op.create_index('idx_projects_status', 'projects', ['project_status'])
    op.create_index('idx_projects_completion_date', 'projects', ['completion_date'])

    op.create_index('idx_buildings_property_id', 'buildings', ['property_id'])
    op.create_index('idx_buildings_area_id', 'buildings', ['area_id'])
    op.create_index('idx_buildings_project_id', 'buildings', ['project_id'])
    op.create_index('idx_buildings_property_type', 'buildings', ['property_type_en'])
    op.create_index('idx_buildings_creation_date', 'buildings', ['creation_date'])

    op.create_index('idx_units_property_id', 'units', ['property_id'])
    op.create_index('idx_units_area_id', 'units', ['area_id'])
    op.create_index('idx_units_project_id', 'units', ['project_id'])
    op.create_index('idx_units_property_type', 'units', ['property_type_en'])
    op.create_index('idx_units_creation_date', 'units', ['creation_date'])

    op.create_index('idx_brokers_participant_id', 'brokers', ['participant_id'])
    op.create_index('idx_brokers_broker_number', 'brokers', ['broker_number'])
    op.create_index('idx_brokers_license_end_date', 'brokers', ['license_end_date'])
    op.create_index('idx_brokers_status', 'brokers', ['status'])

    op.create_index('idx_offices_real_estate_id', 'offices', ['real_estate_id'])
    op.create_index('idx_offices_participant_id', 'offices', ['participant_id'])
    op.create_index('idx_offices_license_expiry', 'offices', ['license_expiry_date'])
    op.create_index('idx_offices_status', 'offices', ['status'])

    op.create_index('idx_valuators_valuator_number', 'valuators', ['valuator_number'])
    op.create_index('idx_valuators_license_end_date', 'valuators', ['license_end_date'])
    op.create_index('idx_valuators_company_number', 'valuators', ['valuation_company_number'])
    op.create_index('idx_valuators_status', 'valuators', ['status'])

    op.create_index('idx_permits_permits_id', 'permits', ['permits_id'])
    op.create_index('idx_permits_permit_number', 'permits', ['permit_number'])
    op.create_index('idx_permits_start_date', 'permits', ['start_date'])
    op.create_index('idx_permits_end_date', 'permits', ['end_date'])
    op.create_index('idx_permits_status', 'permits', ['status'])

    op.create_index('idx_map_requests_request_id', 'map_requests', ['request_id'])
    op.create_index('idx_map_requests_request_date', 'map_requests', ['request_date'])
    op.create_index('idx_map_requests_status', 'map_requests', ['status'])

    op.create_index('idx_rent_contracts_contract_id', 'rent_contracts', ['contract_id'])
    op.create_index('idx_rent_contracts_property_id', 'rent_contracts', ['property_id'])
    op.create_index('idx_rent_contracts_contract_date', 'rent_contracts', ['contract_date'])
    op.create_index('idx_rent_contracts_status', 'rent_contracts', ['contract_status'])

    op.create_index('idx_valuations_valuation_id', 'valuations', ['valuation_id'])
    op.create_index('idx_valuations_property_id', 'valuations', ['property_id'])
    op.create_index('idx_valuations_valuator_id', 'valuations', ['valuator_id'])
    op.create_index('idx_valuations_valuation_date', 'valuations', ['valuation_date'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_valuations_valuation_date', 'valuations')
    op.drop_index('idx_valuations_valuator_id', 'valuations')
    op.drop_index('idx_valuations_property_id', 'valuations')
    op.drop_index('idx_valuations_valuation_id', 'valuations')

    op.drop_index('idx_rent_contracts_status', 'rent_contracts')
    op.drop_index('idx_rent_contracts_contract_date', 'rent_contracts')
    op.drop_index('idx_rent_contracts_property_id', 'rent_contracts')
    op.drop_index('idx_rent_contracts_contract_id', 'rent_contracts')

    op.drop_index('idx_map_requests_status', 'map_requests')
    op.drop_index('idx_map_requests_request_date', 'map_requests')
    op.drop_index('idx_map_requests_request_id', 'map_requests')

    op.drop_index('idx_permits_status', 'permits')
    op.drop_index('idx_permits_end_date', 'permits')
    op.drop_index('idx_permits_start_date', 'permits')
    op.drop_index('idx_permits_permit_number', 'permits')
    op.drop_index('idx_permits_permits_id', 'permits')

    op.drop_index('idx_valuators_status', 'valuators')
    op.drop_index('idx_valuators_company_number', 'valuators')
    op.drop_index('idx_valuators_license_end_date', 'valuators')
    op.drop_index('idx_valuators_valuator_number', 'valuators')

    op.drop_index('idx_offices_status', 'offices')
    op.drop_index('idx_offices_license_expiry', 'offices')
    op.drop_index('idx_offices_participant_id', 'offices')
    op.drop_index('idx_offices_real_estate_id', 'offices')

    op.drop_index('idx_brokers_status', 'brokers')
    op.drop_index('idx_brokers_license_end_date', 'brokers')
    op.drop_index('idx_brokers_broker_number', 'brokers')
    op.drop_index('idx_brokers_participant_id', 'brokers')

    op.drop_index('idx_units_creation_date', 'units')
    op.drop_index('idx_units_property_type', 'units')
    op.drop_index('idx_units_project_id', 'units')
    op.drop_index('idx_units_area_id', 'units')
    op.drop_index('idx_units_property_id', 'units')

    op.drop_index('idx_buildings_creation_date', 'buildings')
    op.drop_index('idx_buildings_property_type', 'buildings')
    op.drop_index('idx_buildings_project_id', 'buildings')
    op.drop_index('idx_buildings_area_id', 'buildings')
    op.drop_index('idx_buildings_property_id', 'buildings')

    op.drop_index('idx_projects_completion_date', 'projects')
    op.drop_index('idx_projects_status', 'projects')
    op.drop_index('idx_projects_developer_id', 'projects')
    op.drop_index('idx_projects_project_id', 'projects')

    op.drop_index('idx_developers_status', 'developers')
    op.drop_index('idx_developers_license_expiry', 'developers')
    op.drop_index('idx_developers_developer_id', 'developers')

    # Drop foreign key constraints
    op.drop_constraint('fk_valuations_valuator_id', 'valuations', type_='foreignkey')
    op.drop_constraint('fk_valuations_property_id', 'valuations', type_='foreignkey')
    op.drop_constraint('fk_offices_participant_id', 'offices', type_='foreignkey')
    op.drop_constraint('fk_units_project_id', 'units', type_='foreignkey')
    op.drop_constraint('fk_units_property_id', 'units', type_='foreignkey')
    op.drop_constraint('fk_buildings_project_id', 'buildings', type_='foreignkey')
    op.drop_constraint('fk_projects_developer_id', 'projects', type_='foreignkey')

    # Drop tables
    op.drop_table('accredited_escrow_agents')
    op.drop_table('real_estate_licenses')
    op.drop_table('licensed_owner_associations')
    op.drop_table('free_zone_companies')
    op.drop_table('valuations')
    op.drop_table('rent_contracts')
    op.drop_table('map_requests')
    op.drop_table('permits')
    op.drop_table('valuators')
    op.drop_table('offices')
    op.drop_table('brokers')
    op.drop_table('units')
    op.drop_table('buildings')
    op.drop_table('projects')
    op.drop_table('developers')
