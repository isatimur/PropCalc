-- PropCalc Database Initialization
-- This file is used to initialize the PostgreSQL database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- Create main tables for DLD data streaming and bulk processing
CREATE TABLE IF NOT EXISTS dld_transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    property_type VARCHAR(100),
    location VARCHAR(200),
    area VARCHAR(200),
    transaction_date DATE,
    price_aed DECIMAL(20,2),
    area_sqft DECIMAL(20,2),
    price_per_sqft DECIMAL(10,2),
    developer_name VARCHAR(200),
    project_name VARCHAR(200),
    property_usage VARCHAR(100),
    property_subtype VARCHAR(100),
    rooms INTEGER,
    parking INTEGER,
    nearest_metro VARCHAR(200),
    nearest_mall VARCHAR(200),
    nearest_landmark VARCHAR(200),
    registration_type VARCHAR(100),
    buyer_nationality VARCHAR(100),
    seller_nationality VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    data_source VARCHAR(100) DEFAULT 'DLD_STREAM'
);

-- Create comprehensive lookup tables for DLD data
CREATE TABLE IF NOT EXISTS dld_areas_lookup (
    area_id VARCHAR(10) PRIMARY KEY,
    name_en VARCHAR(200),
    name_ar VARCHAR(200),
    municipality_number VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS dld_transaction_groups (
    trans_group_id VARCHAR(10) PRIMARY KEY,
    trans_group_ar VARCHAR(200),
    trans_group_en VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS dld_transaction_procedures (
    procedure_id VARCHAR(10) PRIMARY KEY,
    procedure_name_ar VARCHAR(200),
    procedure_name_en VARCHAR(200),
    trans_group_id VARCHAR(10) REFERENCES dld_transaction_groups(trans_group_id)
);

CREATE TABLE IF NOT EXISTS dld_market_types (
    market_type_id VARCHAR(10) PRIMARY KEY,
    market_type_ar VARCHAR(200),
    market_type_en VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS dld_residential_index (
    id SERIAL PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    index_value DECIMAL(10,4),
    index_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_dld_transactions_transaction_id ON dld_transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_dld_transactions_location ON dld_transactions(location);
CREATE INDEX IF NOT EXISTS idx_dld_transactions_date ON dld_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_dld_transactions_developer ON dld_transactions(developer_name);
CREATE INDEX IF NOT EXISTS idx_dld_transactions_processed ON dld_transactions(processed);
CREATE INDEX IF NOT EXISTS idx_dld_transactions_price ON dld_transactions(price_aed);
CREATE INDEX IF NOT EXISTS idx_dld_transactions_data_source ON dld_transactions(data_source);

-- Create indexes for lookup tables
CREATE INDEX IF NOT EXISTS idx_dld_areas_lookup_name ON dld_areas_lookup(name_en);
CREATE INDEX IF NOT EXISTS idx_dld_transaction_groups_name ON dld_transaction_groups(trans_group_en);
CREATE INDEX IF NOT EXISTS idx_dld_transaction_procedures_name ON dld_transaction_procedures(procedure_name_en);
CREATE INDEX IF NOT EXISTS idx_dld_market_types_name ON dld_market_types(market_type_en);
CREATE INDEX IF NOT EXISTS idx_dld_residential_index_date ON dld_residential_index(year, month);

-- Create developers table
CREATE TABLE IF NOT EXISTS developers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    established_year INTEGER,
    track_record_score DECIMAL(5,2) DEFAULT 0.0,
    financial_stability_score DECIMAL(5,2) DEFAULT 0.0,
    customer_satisfaction_score DECIMAL(5,2) DEFAULT 0.0,
    completed_projects_count INTEGER DEFAULT 0,
    total_project_value DECIMAL(15,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    developer_id INTEGER REFERENCES developers(id),
    location VARCHAR(200),
    area VARCHAR(200),
    project_type VARCHAR(100),
    launch_date DATE,
    completion_date DATE,
    total_units INTEGER,
    sold_units INTEGER DEFAULT 0,
    avg_price_per_sqft DECIMAL(10,2),
    min_price DECIMAL(15,2),
    max_price DECIMAL(15,2),
    vantage_score DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for projects
CREATE INDEX IF NOT EXISTS idx_projects_developer_id ON projects(developer_id);
CREATE INDEX IF NOT EXISTS idx_projects_location ON projects(location);
CREATE INDEX IF NOT EXISTS idx_projects_vantage_score ON projects(vantage_score);

-- Create data processing log table for tracking CSV imports
CREATE TABLE IF NOT EXISTS data_processing_log (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    file_size BIGINT,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    processing_status VARCHAR(50) DEFAULT 'PENDING',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_duration_seconds INTEGER
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_dld_transactions_updated_at 
    BEFORE UPDATE ON dld_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_developers_updated_at 
    BEFORE UPDATE ON developers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO developers (name, established_year, track_record_score, financial_stability_score, customer_satisfaction_score, completed_projects_count, total_project_value) VALUES
('Emaar Properties', 1997, 9.2, 9.5, 8.8, 150, 50000000000),
('Nakheel', 2000, 8.8, 8.9, 8.5, 120, 35000000000),
('Damac Properties', 2002, 8.5, 8.2, 8.0, 80, 25000000000),
('Meraas', 2007, 8.0, 8.5, 8.2, 45, 15000000000),
('Sobha Realty', 2003, 8.8, 8.7, 8.9, 65, 20000000000)
ON CONFLICT (name) DO NOTHING;

INSERT INTO projects (name, developer_id, location, area, project_type, launch_date, total_units, avg_price_per_sqft, vantage_score) VALUES
('Burj Khalifa', 1, 'Downtown Dubai', 'Downtown', 'Residential', '2004-01-01', 900, 2500.00, 9.8),
('Palm Jumeirah', 2, 'Palm Jumeirah', 'Palm Jumeirah', 'Mixed Use', '2001-01-01', 1500, 1800.00, 9.5),
('Marina Gate', 1, 'Dubai Marina', 'Dubai Marina', 'Residential', '2008-01-01', 800, 2200.00, 9.2),
('Binghatti Rose', 3, 'Business Bay', 'Business Bay', 'Residential', '2019-01-01', 400, 1600.00, 8.8),
('Bluewaters Island', 4, 'Bluewaters', 'Bluewaters', 'Mixed Use', '2016-01-01', 600, 2000.00, 8.9)
ON CONFLICT DO NOTHING;

-- Create comprehensive analytics view
CREATE OR REPLACE VIEW dld_analytics_summary AS
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT transaction_id) as unique_transactions,
    COUNT(DISTINCT location) as unique_locations,
    COUNT(DISTINCT developer_name) as unique_developers,
    COUNT(DISTINCT property_type) as unique_property_types,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    AVG(price_aed) as avg_price,
    SUM(price_aed) as total_volume,
    AVG(area_sqft) as avg_area,
    AVG(price_per_sqft) as avg_price_per_sqft,
    data_source
FROM dld_transactions 
GROUP BY data_source;

-- Basic health check
SELECT 'PropCalc Database Initialized Successfully with DLD streaming tables' as message;
