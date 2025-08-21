-- Create area mapping system for PropCalc
-- This will map DLD area names to internet-friendly names and create region hierarchy

-- Create area mapping table
CREATE TABLE IF NOT EXISTS area_mapping (
    id SERIAL PRIMARY KEY,
    dld_area_id VARCHAR(10) REFERENCES dld_areas_lookup(area_id),
    dld_area_name VARCHAR(200),
    internet_name VARCHAR(200) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    region_category VARCHAR(100), -- e.g., 'Downtown', 'Marina', 'Suburban'
    municipality VARCHAR(100),
    popularity_score INTEGER DEFAULT 0, -- Based on transaction volume
    avg_price_aed NUMERIC(15,2),
    min_price_aed NUMERIC(15,2),
    max_price_aed NUMERIC(15,2),
    price_trend VARCHAR(50), -- 'rising', 'stable', 'declining'
    transaction_volume INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create region hierarchy table
CREATE TABLE IF NOT EXISTS region_hierarchy (
    id SERIAL PRIMARY KEY,
    parent_region_id INTEGER REFERENCES region_hierarchy(id),
    region_name VARCHAR(200) NOT NULL,
    region_type VARCHAR(100), -- 'city', 'district', 'neighborhood'
    level INTEGER DEFAULT 1, -- Hierarchy level
    coordinates_lat NUMERIC(10,8),
    coordinates_lng NUMERIC(10,8),
    bounding_box TEXT, -- JSON format for map boundaries
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create area analytics table for caching
CREATE TABLE IF NOT EXISTS area_analytics (
    id SERIAL PRIMARY KEY,
    area_mapping_id INTEGER REFERENCES area_mapping(id),
    analysis_date DATE NOT NULL,
    total_transactions INTEGER DEFAULT 0,
    total_volume_aed NUMERIC(20,2),
    avg_price_aed NUMERIC(15,2),
    median_price_aed NUMERIC(15,2),
    min_price_aed NUMERIC(15,2),
    max_price_aed NUMERIC(15,2),
    price_per_sqft_avg NUMERIC(12,2),
    transaction_trend VARCHAR(50),
    market_sentiment VARCHAR(50),
    top_property_types JSONB,
    top_developers JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_area_mapping_internet_name ON area_mapping(internet_name);
CREATE INDEX IF NOT EXISTS idx_area_mapping_normalized_name ON area_mapping(normalized_name);
CREATE INDEX IF NOT EXISTS idx_area_mapping_region_category ON area_mapping(region_category);
CREATE INDEX IF NOT EXISTS idx_area_analytics_date ON area_analytics(analysis_date);
CREATE INDEX IF NOT EXISTS idx_area_analytics_area ON area_analytics(area_mapping_id);

-- Insert initial area mappings for popular Dubai areas
INSERT INTO area_mapping (dld_area_name, internet_name, normalized_name, region_category, municipality, popularity_score) VALUES
-- Downtown Dubai
('Downtown Dubai', 'Downtown Dubai', 'downtown_dubai', 'Downtown', 'Dubai Municipality', 95),
('Burj Khalifa', 'Burj Khalifa', 'burj_khalifa', 'Downtown', 'Dubai Municipality', 90),
('The Address', 'The Address', 'the_address', 'Downtown', 'Dubai Municipality', 85),

-- Dubai Marina
('Dubai Marina', 'Dubai Marina', 'dubai_marina', 'Marina', 'Dubai Municipality', 98),
('Marina Gate', 'Marina Gate', 'marina_gate', 'Marina', 'Dubai Municipality', 92),
('Marina Heights', 'Marina Heights', 'marina_heights', 'Marina', 'Dubai Municipality', 88),

-- Palm Jumeirah
('Palm Jumeirah', 'Palm Jumeirah', 'palm_jumeirah', 'Island', 'Dubai Municipality', 96),
('Palm Tower', 'Palm Tower', 'palm_tower', 'Island', 'Dubai Municipality', 94),
('Atlantis', 'Atlantis', 'atlantis', 'Island', 'Dubai Municipality', 89),

-- Business Bay
('Business Bay', 'Business Bay', 'business_bay', 'Business', 'Dubai Municipality', 87),
('Bay Square', 'Bay Square', 'bay_square', 'Business', 'Dubai Municipality', 82),

-- JBR
('Jumeirah Beach Residence', 'JBR', 'jbr', 'Beach', 'Dubai Municipality', 93),
('The Walk', 'The Walk JBR', 'the_walk_jbr', 'Beach', 'Dubai Municipality', 89),

-- Other popular areas
('Al Barsha', 'Al Barsha', 'al_barsha', 'Suburban', 'Dubai Municipality', 78),
('Al Barsha First', 'Al Barsha 1', 'al_barsha_1', 'Suburban', 'Dubai Municipality', 75),
('Al Barsha Second', 'Al Barsha 2', 'al_barsha_2', 'Suburban', 'Dubai Municipality', 72),
('Al Barsha Third', 'Al Barsha 3', 'al_barsha_3', 'Suburban', 'Dubai Municipality', 70),

-- Insert more mappings as needed
('Al Barshaa South First', 'Al Barsha South 1', 'al_barsha_south_1', 'Suburban', 'Dubai Municipality', 68),
('Al Barshaa South Second', 'Al Barsha South 2', 'al_barsha_south_2', 'Suburban', 'Dubai Municipality', 65),
('Al Barshaa South Third', 'Al Barsha South 3', 'al_barsha_south_3', 'Suburban', 'Dubai Municipality', 63);

-- Create function to update area analytics
CREATE OR REPLACE FUNCTION update_area_analytics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update area analytics when transactions are modified
    INSERT INTO area_analytics (
        area_mapping_id,
        analysis_date,
        total_transactions,
        total_volume_aed,
        avg_price_aed,
        median_price_aed,
        min_price_aed,
        max_price_aed,
        price_per_sqft_avg
    )
    SELECT 
        am.id,
        CURRENT_DATE,
        COUNT(dt.id),
        SUM(dt.price_aed),
        AVG(dt.price_aed),
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dt.price_aed),
        MIN(dt.price_aed),
        MAX(dt.price_aed),
        AVG(dt.price_per_sqft)
    FROM dld_transactions dt
    JOIN area_mapping am ON LOWER(dt.location) = LOWER(am.dld_area_name)
    WHERE dt.location = COALESCE(NEW.location, OLD.location)
    GROUP BY am.id
    ON CONFLICT (area_mapping_id, analysis_date) 
    DO UPDATE SET
        total_transactions = EXCLUDED.total_transactions,
        total_volume_aed = EXCLUDED.total_volume_aed,
        avg_price_aed = EXCLUDED.avg_price_aed,
        median_price_aed = EXCLUDED.median_price_aed,
        min_price_aed = EXCLUDED.min_price_aed,
        max_price_aed = EXCLUDED.max_price_aed,
        price_per_sqft_avg = EXCLUDED.price_per_sqft_avg,
        created_at = CURRENT_TIMESTAMP;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update analytics
CREATE TRIGGER trigger_update_area_analytics
    AFTER INSERT OR UPDATE OR DELETE ON dld_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_area_analytics();

-- Create view for easy access to area data
CREATE OR REPLACE VIEW area_overview AS
SELECT 
    am.id,
    am.dld_area_name,
    am.internet_name,
    am.normalized_name,
    am.region_category,
    am.municipality,
    am.popularity_score,
    am.avg_price_aed,
    am.min_price_aed,
    am.max_price_aed,
    am.price_trend,
    am.transaction_volume,
    aa.total_transactions,
    aa.total_volume_aed,
    aa.median_price_aed,
    aa.price_per_sqft_avg,
    aa.market_sentiment,
    aa.last_updated
FROM area_mapping am
LEFT JOIN area_analytics aa ON am.id = aa.area_mapping_id
WHERE aa.analysis_date = (
    SELECT MAX(analysis_date) 
    FROM area_analytics aa2 
    WHERE aa2.area_mapping_id = am.id
);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vantage_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vantage_user;
