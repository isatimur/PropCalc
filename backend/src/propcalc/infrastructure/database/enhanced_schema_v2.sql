-- Enhanced Database Schema v2.0 for PropCalc
-- Comprehensive schema for all new CSV data sources
-- Includes proper relationships, indexes, and constraints

-- =====================================================
-- CORE TABLES
-- =====================================================

-- DEVELOPERS TABLE
CREATE TABLE IF NOT EXISTS developers (
    id SERIAL PRIMARY KEY,
    developer_id VARCHAR(50) UNIQUE NOT NULL,
    developer_number VARCHAR(50),
    developer_name_ar VARCHAR(255),
    developer_name_en VARCHAR(255),
    developer_type VARCHAR(100),
    license_number VARCHAR(50),
    license_issue_date DATE,
    license_expiry_date DATE,
    status VARCHAR(50),
    contact_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PROJECTS TABLE
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) UNIQUE NOT NULL,
    project_number VARCHAR(50),
    project_name_ar VARCHAR(255),
    project_name_en VARCHAR(255),
    developer_id VARCHAR(50) REFERENCES developers(developer_id),
    developer_name VARCHAR(255),
    master_developer_id VARCHAR(50),
    master_developer_name VARCHAR(255),
    project_start_date DATE,
    project_end_date DATE,
    project_type_id INTEGER,
    project_type_ar VARCHAR(100),
    project_type_en VARCHAR(100),
    project_classification_id INTEGER,
    project_classification_ar VARCHAR(100),
    project_classification_en VARCHAR(100),
    escrow_agent_id VARCHAR(50),
    escrow_agent_name VARCHAR(255),
    project_status VARCHAR(50),
    project_status_ar VARCHAR(100),
    project_status_en VARCHAR(100),
    percent_completed DECIMAL(5,2),
    completion_date DATE,
    cancellation_date DATE,
    project_description_ar TEXT,
    project_description_en TEXT,
    property_id VARCHAR(50),
    area_id INTEGER,
    area_name_ar VARCHAR(255),
    area_name_en VARCHAR(255),
    master_project_ar VARCHAR(255),
    master_project_en VARCHAR(255),
    zoning_authority_id INTEGER,
    zoning_authority_ar VARCHAR(100),
    zoning_authority_en VARCHAR(100),
    no_of_lands INTEGER,
    no_of_buildings INTEGER,
    no_of_villas INTEGER,
    no_of_units INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BUILDINGS TABLE
CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(50) UNIQUE NOT NULL,
    area_id INTEGER,
    zone_id INTEGER,
    area_name_ar VARCHAR(255),
    area_name_en VARCHAR(255),
    land_number VARCHAR(50),
    land_sub_number VARCHAR(50),
    building_number VARCHAR(50),
    common_area DECIMAL(10,2),
    actual_common_area DECIMAL(10,2),
    floors INTEGER,
    rooms VARCHAR(50),
    rooms_ar VARCHAR(100),
    rooms_en VARCHAR(100),
    car_parks INTEGER,
    built_up_area DECIMAL(10,2),
    bld_levels INTEGER,
    shops INTEGER,
    flats INTEGER,
    offices INTEGER,
    swimming_pools INTEGER,
    elevators INTEGER,
    actual_area DECIMAL(10,2),
    property_type_id INTEGER,
    property_type_ar VARCHAR(100),
    property_type_en VARCHAR(100),
    property_sub_type_id INTEGER,
    property_sub_type_ar VARCHAR(100),
    property_sub_type_en VARCHAR(100),
    parent_property_id VARCHAR(50),
    creation_date DATE,
    parcel_id VARCHAR(50),
    is_free_hold BOOLEAN DEFAULT FALSE,
    is_lease_hold BOOLEAN DEFAULT FALSE,
    is_registered BOOLEAN DEFAULT FALSE,
    pre_registration_number VARCHAR(50),
    master_project_id VARCHAR(50),
    master_project_en VARCHAR(255),
    master_project_ar VARCHAR(255),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    project_name_ar VARCHAR(255),
    project_name_en VARCHAR(255),
    land_type_id INTEGER,
    land_type_ar VARCHAR(100),
    land_type_en VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UNITS TABLE
CREATE TABLE IF NOT EXISTS units (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(50) REFERENCES buildings(property_id),
    area_id INTEGER,
    zone_id INTEGER,
    area_name_ar VARCHAR(255),
    area_name_en VARCHAR(255),
    land_number VARCHAR(50),
    building_number VARCHAR(50),
    unit_number VARCHAR(50),
    unit_balcony_area DECIMAL(10,2),
    unit_parking_number VARCHAR(50),
    floor VARCHAR(20),
    rooms VARCHAR(50),
    actual_area DECIMAL(10,2),
    property_type_id INTEGER,
    property_type_ar VARCHAR(100),
    property_type_en VARCHAR(100),
    property_sub_type_id INTEGER,
    property_sub_type_ar VARCHAR(100),
    property_sub_type_en VARCHAR(100),
    master_project_id VARCHAR(50),
    master_project_en VARCHAR(255),
    project_id VARCHAR(50) REFERENCES projects(project_id),
    project_name_en VARCHAR(255),
    land_type_id INTEGER,
    land_type_en VARCHAR(100),
    creation_date DATE,
    is_free_hold BOOLEAN DEFAULT FALSE,
    is_lease_hold BOOLEAN DEFAULT FALSE,
    is_registered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- BROKERAGE AND LICENSING TABLES
-- =====================================================

-- BROKERS TABLE
CREATE TABLE IF NOT EXISTS brokers (
    id SERIAL PRIMARY KEY,
    participant_id VARCHAR(50) UNIQUE NOT NULL,
    real_estate_broker_id VARCHAR(50),
    broker_number VARCHAR(50) UNIQUE,
    broker_name_ar VARCHAR(255),
    broker_name_en VARCHAR(255),
    gender VARCHAR(10),
    license_start_date DATE,
    license_end_date DATE,
    webpage VARCHAR(255),
    phone VARCHAR(50),
    fax VARCHAR(50),
    real_estate_id VARCHAR(50),
    real_estate_number VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OFFICES TABLE
CREATE TABLE IF NOT EXISTS offices (
    id SERIAL PRIMARY KEY,
    participant_id VARCHAR(50) REFERENCES brokers(participant_id),
    real_estate_id VARCHAR(50) UNIQUE NOT NULL,
    real_estate_number VARCHAR(50),
    license_source_id INTEGER,
    license_source_ar VARCHAR(100),
    license_source_en VARCHAR(100),
    license_number VARCHAR(50),
    license_issue_date DATE,
    license_expiry_date DATE,
    is_branch BOOLEAN DEFAULT FALSE,
    main_office_id VARCHAR(50),
    webpage VARCHAR(255),
    phone VARCHAR(50),
    fax VARCHAR(50),
    activity_type_id INTEGER,
    ded_activity_code VARCHAR(20),
    activity_type_ar VARCHAR(100),
    activity_type_en VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VALUATORS TABLE
CREATE TABLE IF NOT EXISTS valuators (
    id SERIAL PRIMARY KEY,
    valuation_company_number VARCHAR(50),
    valuation_company_name_ar VARCHAR(255),
    valuation_company_name_en VARCHAR(255),
    valuator_number VARCHAR(50) UNIQUE,
    valuator_name_ar VARCHAR(255),
    valuator_name_en VARCHAR(255),
    valuator_nationality_id INTEGER,
    valuator_nationality_en VARCHAR(100),
    gender_id INTEGER,
    gender_en VARCHAR(20),
    license_start_date DATE,
    license_end_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PERMITS AND REGULATORY TABLES
-- =====================================================

-- PERMITS TABLE
CREATE TABLE IF NOT EXISTS permits (
    id SERIAL PRIMARY KEY,
    permits_id VARCHAR(50) UNIQUE NOT NULL,
    permit_number VARCHAR(50),
    start_date DATE,
    end_date DATE,
    location TEXT,
    exhibition_name_ar VARCHAR(255),
    exhibition_name_en VARCHAR(255),
    permit_status_id INTEGER,
    permit_status_en VARCHAR(100),
    parent_service_id INTEGER,
    main_service_en VARCHAR(255),
    service_id INTEGER,
    service_ar VARCHAR(100),
    service_en VARCHAR(100),
    sub_service_id INTEGER,
    sub_service_ar VARCHAR(100),
    sub_service_en VARCHAR(100),
    applicant_id VARCHAR(50),
    applicant_name_ar VARCHAR(255),
    applicant_name_en VARCHAR(255),
    applicant_type_id INTEGER,
    applicant_type_ar VARCHAR(100),
    applicant_type_en VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MAP_REQUESTS TABLE
CREATE TABLE IF NOT EXISTS map_requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(50) UNIQUE NOT NULL,
    request_date TIMESTAMP,
    application_id INTEGER,
    application_ar VARCHAR(100),
    sub_service_application_en VARCHAR(100),
    request_source_id INTEGER,
    request_source_ar VARCHAR(100),
    request_source_en VARCHAR(100),
    procedure_id INTEGER,
    procedure_name_ar VARCHAR(100),
    procedure_name_en VARCHAR(100),
    property_type_id INTEGER,
    property_type_ar VARCHAR(100),
    property_type_en VARCHAR(100),
    no_of_siteplans INTEGER,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CONTRACTS AND VALUATION TABLES
-- =====================================================

-- RENT_CONTRACTS TABLE (Large table - optimized)
CREATE TABLE IF NOT EXISTS rent_contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) UNIQUE NOT NULL,
    contract_number VARCHAR(50),
    contract_date DATE,
    contract_type VARCHAR(100),
    property_id VARCHAR(50),
    unit_id VARCHAR(50),
    tenant_id VARCHAR(50),
    tenant_name_ar VARCHAR(255),
    tenant_name_en VARCHAR(255),
    landlord_id VARCHAR(50),
    landlord_name_ar VARCHAR(255),
    landlord_name_en VARCHAR(255),
    rent_amount DECIMAL(15,2),
    rent_currency VARCHAR(10),
    contract_start_date DATE,
    contract_end_date DATE,
    contract_status VARCHAR(50),
    area_sqft DECIMAL(10,2),
    bedrooms INTEGER,
    bathrooms INTEGER,
    parking_spaces INTEGER,
    location_ar VARCHAR(255),
    location_en VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VALUATION TABLE
CREATE TABLE IF NOT EXISTS valuations (
    id SERIAL PRIMARY KEY,
    valuation_id VARCHAR(50) UNIQUE NOT NULL,
    property_id VARCHAR(50) REFERENCES buildings(property_id),
    valuator_id VARCHAR(50) REFERENCES valuators(valuator_number),
    valuation_date DATE,
    valuation_amount DECIMAL(15,2),
    valuation_currency VARCHAR(10),
    valuation_type VARCHAR(100),
    valuation_method VARCHAR(100),
    valuation_status VARCHAR(50),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- LICENSING AND REGULATORY TABLES
-- =====================================================

-- FREE_ZONE_COMPANIES TABLE
CREATE TABLE IF NOT EXISTS free_zone_companies (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) UNIQUE NOT NULL,
    company_name_ar VARCHAR(255),
    company_name_en VARCHAR(255),
    license_number VARCHAR(50),
    license_issue_date DATE,
    license_expiry_date DATE,
    free_zone_name VARCHAR(100),
    activity_type VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LICENSED_OWNER_ASSOCIATIONS TABLE
CREATE TABLE IF NOT EXISTS licensed_owner_associations (
    id SERIAL PRIMARY KEY,
    association_id VARCHAR(50) UNIQUE NOT NULL,
    association_name_ar VARCHAR(255),
    association_name_en VARCHAR(255),
    license_number VARCHAR(50),
    license_issue_date DATE,
    license_expiry_date DATE,
    contact_info JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- REAL_ESTATE_LICENSES TABLE
CREATE TABLE IF NOT EXISTS real_estate_licenses (
    id SERIAL PRIMARY KEY,
    license_id VARCHAR(50) UNIQUE NOT NULL,
    license_number VARCHAR(50),
    license_type VARCHAR(100),
    licensee_name_ar VARCHAR(255),
    licensee_name_en VARCHAR(255),
    license_issue_date DATE,
    license_expiry_date DATE,
    activity_type VARCHAR(100),
    status VARCHAR(50),
    contact_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ACCREDITED_ESCROW_AGENTS TABLE
CREATE TABLE IF NOT EXISTS accredited_escrow_agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    agent_name_ar VARCHAR(255),
    agent_name_en VARCHAR(255),
    license_number VARCHAR(50),
    license_issue_date DATE,
    license_expiry_date DATE,
    contact_info JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Developers indexes
CREATE INDEX IF NOT EXISTS idx_developers_developer_id ON developers(developer_id);
CREATE INDEX IF NOT EXISTS idx_developers_license_expiry ON developers(license_expiry_date);
CREATE INDEX IF NOT EXISTS idx_developers_status ON developers(status);

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_project_id ON projects(project_id);
CREATE INDEX IF NOT EXISTS idx_projects_developer_id ON projects(developer_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(project_status);
CREATE INDEX IF NOT EXISTS idx_projects_completion_date ON projects(completion_date);

-- Buildings indexes
CREATE INDEX IF NOT EXISTS idx_buildings_property_id ON buildings(property_id);
CREATE INDEX IF NOT EXISTS idx_buildings_area_id ON buildings(area_id);
CREATE INDEX IF NOT EXISTS idx_buildings_project_id ON buildings(project_id);
CREATE INDEX IF NOT EXISTS idx_buildings_property_type ON buildings(property_type_en);
CREATE INDEX IF NOT EXISTS idx_buildings_creation_date ON buildings(creation_date);

-- Units indexes
CREATE INDEX IF NOT EXISTS idx_units_property_id ON units(property_id);
CREATE INDEX IF NOT EXISTS idx_units_area_id ON units(area_id);
CREATE INDEX IF NOT EXISTS idx_units_project_id ON units(project_id);
CREATE INDEX IF NOT EXISTS idx_units_property_type ON units(property_type_en);
CREATE INDEX IF NOT EXISTS idx_units_creation_date ON units(creation_date);

-- Brokers indexes
CREATE INDEX IF NOT EXISTS idx_brokers_participant_id ON brokers(participant_id);
CREATE INDEX IF NOT EXISTS idx_brokers_broker_number ON brokers(broker_number);
CREATE INDEX IF NOT EXISTS idx_brokers_license_end_date ON brokers(license_end_date);
CREATE INDEX IF NOT EXISTS idx_brokers_status ON brokers(status);

-- Offices indexes
CREATE INDEX IF NOT EXISTS idx_offices_real_estate_id ON offices(real_estate_id);
CREATE INDEX IF NOT EXISTS idx_offices_participant_id ON offices(participant_id);
CREATE INDEX IF NOT EXISTS idx_offices_license_expiry ON offices(license_expiry_date);
CREATE INDEX IF NOT EXISTS idx_offices_status ON offices(status);

-- Valuators indexes
CREATE INDEX IF NOT EXISTS idx_valuators_valuator_number ON valuators(valuator_number);
CREATE INDEX IF NOT EXISTS idx_valuators_license_end_date ON valuators(license_end_date);
CREATE INDEX IF NOT EXISTS idx_valuators_company_number ON valuators(valuation_company_number);
CREATE INDEX IF NOT EXISTS idx_valuators_status ON valuators(status);

-- Permits indexes
CREATE INDEX IF NOT EXISTS idx_permits_permits_id ON permits(permits_id);
CREATE INDEX IF NOT EXISTS idx_permits_permit_number ON permits(permit_number);
CREATE INDEX IF NOT EXISTS idx_permits_start_date ON permits(start_date);
CREATE INDEX IF NOT EXISTS idx_permits_end_date ON permits(end_date);
CREATE INDEX IF NOT EXISTS idx_permits_status ON permits(status);

-- Map requests indexes
CREATE INDEX IF NOT EXISTS idx_map_requests_request_id ON map_requests(request_id);
CREATE INDEX IF NOT EXISTS idx_map_requests_request_date ON map_requests(request_date);
CREATE INDEX IF NOT EXISTS idx_map_requests_status ON map_requests(status);

-- Rent contracts indexes
CREATE INDEX IF NOT EXISTS idx_rent_contracts_contract_id ON rent_contracts(contract_id);
CREATE INDEX IF NOT EXISTS idx_rent_contracts_property_id ON rent_contracts(property_id);
CREATE INDEX IF NOT EXISTS idx_rent_contracts_contract_date ON rent_contracts(contract_date);
CREATE INDEX IF NOT EXISTS idx_rent_contracts_status ON rent_contracts(contract_status);

-- Valuations indexes
CREATE INDEX IF NOT EXISTS idx_valuations_valuation_id ON valuations(valuation_id);
CREATE INDEX IF NOT EXISTS idx_valuations_property_id ON valuations(property_id);
CREATE INDEX IF NOT EXISTS idx_valuations_valuator_id ON valuations(valuator_id);
CREATE INDEX IF NOT EXISTS idx_valuations_valuation_date ON valuations(valuation_date);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables
CREATE TRIGGER update_developers_updated_at BEFORE UPDATE ON developers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_buildings_updated_at BEFORE UPDATE ON buildings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_units_updated_at BEFORE UPDATE ON units FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_brokers_updated_at BEFORE UPDATE ON brokers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_offices_updated_at BEFORE UPDATE ON offices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_valuators_updated_at BEFORE UPDATE ON valuators FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_permits_updated_at BEFORE UPDATE ON permits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_map_requests_updated_at BEFORE UPDATE ON map_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rent_contracts_updated_at BEFORE UPDATE ON rent_contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_valuations_updated_at BEFORE UPDATE ON valuations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_free_zone_companies_updated_at BEFORE UPDATE ON free_zone_companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_licensed_owner_associations_updated_at BEFORE UPDATE ON licensed_owner_associations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_real_estate_licenses_updated_at BEFORE UPDATE ON real_estate_licenses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accredited_escrow_agents_updated_at BEFORE UPDATE ON accredited_escrow_agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Active developers view
CREATE OR REPLACE VIEW active_developers AS
SELECT 
    developer_id,
    developer_name_en,
    developer_name_ar,
    license_number,
    license_expiry_date,
    status
FROM developers 
WHERE status = 'ACTIVE' 
AND (license_expiry_date IS NULL OR license_expiry_date > CURRENT_DATE);

-- Active projects view
CREATE OR REPLACE VIEW active_projects AS
SELECT 
    p.project_id,
    p.project_name_en,
    p.project_name_ar,
    p.developer_name,
    p.project_status,
    p.percent_completed,
    p.completion_date,
    p.no_of_units,
    p.area_name_en
FROM projects p
WHERE p.project_status IN ('ACTIVE', 'IN_PROGRESS', 'PLANNING');

-- Property summary view
CREATE OR REPLACE VIEW property_summary AS
SELECT 
    b.property_id,
    b.area_name_en,
    b.property_type_en,
    b.actual_area,
    b.is_free_hold,
    b.is_registered,
    p.project_name_en,
    d.developer_name_en,
    COUNT(u.id) as unit_count
FROM buildings b
LEFT JOIN projects p ON b.project_id = p.project_id
LEFT JOIN developers d ON p.developer_id = d.developer_id
LEFT JOIN units u ON b.property_id = u.property_id
GROUP BY b.property_id, b.area_name_en, b.property_type_en, b.actual_area, 
         b.is_free_hold, b.is_registered, p.project_name_en, d.developer_name_en;

-- Active brokers view
CREATE OR REPLACE VIEW active_brokers AS
SELECT 
    b.participant_id,
    b.broker_name_en,
    b.broker_name_ar,
    b.broker_number,
    b.license_end_date,
    o.real_estate_id,
    o.activity_type_en
FROM brokers b
LEFT JOIN offices o ON b.participant_id = o.participant_id
WHERE b.license_end_date > CURRENT_DATE
AND b.status = 'ACTIVE';

-- Market activity view
CREATE OR REPLACE VIEW market_activity AS
SELECT 
    'RENT_CONTRACTS' as activity_type,
    contract_date as activity_date,
    COUNT(*) as activity_count,
    SUM(rent_amount) as total_value
FROM rent_contracts 
WHERE contract_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY contract_date
UNION ALL
SELECT 
    'VALUATIONS' as activity_type,
    valuation_date as activity_date,
    COUNT(*) as activity_count,
    SUM(valuation_amount) as total_value
FROM valuations 
WHERE valuation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY valuation_date;

-- =====================================================
-- ANALYTICS FUNCTIONS
-- =====================================================

-- Function to get market statistics
CREATE OR REPLACE FUNCTION get_market_statistics(
    p_area_id INTEGER DEFAULT NULL,
    p_property_type VARCHAR(100) DEFAULT NULL,
    p_date_from DATE DEFAULT CURRENT_DATE - INTERVAL '90 days',
    p_date_to DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    total_properties INTEGER,
    total_units INTEGER,
    avg_rent_amount DECIMAL(15,2),
    avg_valuation_amount DECIMAL(15,2),
    total_contracts INTEGER,
    total_valuations INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT b.property_id)::INTEGER as total_properties,
        COUNT(DISTINCT u.id)::INTEGER as total_units,
        AVG(rc.rent_amount) as avg_rent_amount,
        AVG(v.valuation_amount) as avg_valuation_amount,
        COUNT(DISTINCT rc.contract_id)::INTEGER as total_contracts,
        COUNT(DISTINCT v.valuation_id)::INTEGER as total_valuations
    FROM buildings b
    LEFT JOIN units u ON b.property_id = u.property_id
    LEFT JOIN rent_contracts rc ON u.property_id = rc.property_id 
        AND rc.contract_date BETWEEN p_date_from AND p_date_to
    LEFT JOIN valuations v ON b.property_id = v.property_id 
        AND v.valuation_date BETWEEN p_date_from AND p_date_to
    WHERE (p_area_id IS NULL OR b.area_id = p_area_id)
    AND (p_property_type IS NULL OR b.property_type_en = p_property_type);
END;
$$ LANGUAGE plpgsql;

-- Function to get developer performance
CREATE OR REPLACE FUNCTION get_developer_performance(
    p_developer_id VARCHAR(50) DEFAULT NULL
)
RETURNS TABLE(
    developer_id VARCHAR(50),
    developer_name VARCHAR(255),
    total_projects INTEGER,
    completed_projects INTEGER,
    total_units INTEGER,
    avg_project_completion_rate DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.developer_id,
        d.developer_name_en,
        COUNT(p.project_id)::INTEGER as total_projects,
        COUNT(CASE WHEN p.project_status = 'FINISHED' THEN 1 END)::INTEGER as completed_projects,
        SUM(p.no_of_units)::INTEGER as total_units,
        AVG(p.percent_completed) as avg_project_completion_rate
    FROM developers d
    LEFT JOIN projects p ON d.developer_id = p.developer_id
    WHERE (p_developer_id IS NULL OR d.developer_id = p_developer_id)
    GROUP BY d.developer_id, d.developer_name_en;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- DATA QUALITY CHECKS
-- =====================================================

-- Function to check data quality
CREATE OR REPLACE FUNCTION check_data_quality()
RETURNS TABLE(
    table_name VARCHAR(100),
    total_records BIGINT,
    null_percentage DECIMAL(5,2),
    duplicate_percentage DECIMAL(5,2),
    quality_score DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'developers'::VARCHAR(100) as table_name,
        COUNT(*) as total_records,
        (COUNT(*) FILTER (WHERE developer_id IS NULL) * 100.0 / COUNT(*)) as null_percentage,
        0 as duplicate_percentage,
        100 - (COUNT(*) FILTER (WHERE developer_id IS NULL) * 100.0 / COUNT(*)) as quality_score
    FROM developers
    UNION ALL
    SELECT 
        'projects'::VARCHAR(100) as table_name,
        COUNT(*) as total_records,
        (COUNT(*) FILTER (WHERE project_id IS NULL) * 100.0 / COUNT(*)) as null_percentage,
        0 as duplicate_percentage,
        100 - (COUNT(*) FILTER (WHERE project_id IS NULL) * 100.0 / COUNT(*)) as quality_score
    FROM projects
    UNION ALL
    SELECT 
        'buildings'::VARCHAR(100) as table_name,
        COUNT(*) as total_records,
        (COUNT(*) FILTER (WHERE property_id IS NULL) * 100.0 / COUNT(*)) as null_percentage,
        0 as duplicate_percentage,
        100 - (COUNT(*) FILTER (WHERE property_id IS NULL) * 100.0 / COUNT(*)) as quality_score
    FROM buildings;
END;
$$ LANGUAGE plpgsql; 