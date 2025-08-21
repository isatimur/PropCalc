-- Populate area analytics with real data from DLD transactions
-- This will create analytics for all mapped areas

-- First, let's update area_mapping with real DLD area names from transactions
UPDATE area_mapping 
SET dld_area_name = CASE 
    WHEN internet_name = 'Al Barsha' THEN 'Al Barsha'
    WHEN internet_name = 'Al Barsha 1' THEN 'Al Barsha First'
    WHEN internet_name = 'Al Barsha 2' THEN 'Al Barsha Second'
    WHEN internet_name = 'Al Barsha 3' THEN 'Al Barsha Third'
    WHEN internet_name = 'Al Barsha South 1' THEN 'Al Barshaa South First'
    WHEN internet_name = 'Al Barsha South 2' THEN 'Al Barshaa South Second'
    WHEN internet_name = 'Al Barsha South 3' THEN 'Al Barshaa South Third'
    ELSE dld_area_name
END;

-- Now populate area_analytics with real data
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
    COUNT(dt.id) as total_transactions,
    SUM(dt.price_aed) as total_volume_aed,
    AVG(dt.price_aed) as avg_price_aed,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dt.price_aed) as median_price_aed,
    MIN(dt.price_aed) as min_price_aed,
    MAX(dt.price_aed) as max_price_aed,
    AVG(dt.price_per_sqft) as price_per_sqft_avg
FROM area_mapping am
JOIN dld_transactions dt ON LOWER(dt.location) = LOWER(am.dld_area_name)
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

-- Update area_mapping with calculated values
UPDATE area_mapping 
SET 
    avg_price_aed = aa.avg_price_aed,
    min_price_aed = aa.min_price_aed,
    max_price_aed = aa.max_price_aed,
    transaction_volume = aa.total_transactions,
    last_updated = CURRENT_TIMESTAMP
FROM area_analytics aa
WHERE aa.area_mapping_id = area_mapping.id
AND aa.analysis_date = CURRENT_DATE;

-- Update popularity scores based on transaction volume
UPDATE area_mapping 
SET popularity_score = CASE
    WHEN transaction_volume > 1000 THEN 100
    WHEN transaction_volume > 500 THEN 80
    WHEN transaction_volume > 100 THEN 60
    WHEN transaction_volume > 50 THEN 40
    WHEN transaction_volume > 10 THEN 20
    ELSE 10
END;

-- Add more area mappings for popular DLD areas
INSERT INTO area_mapping (dld_area_name, internet_name, normalized_name, region_category, municipality, popularity_score) VALUES
-- More Al Barsha areas
('Al Barsha Fourth', 'Al Barsha 4', 'al_barsha_4', 'Suburban', 'Dubai Municipality', 60),
('Al Barsha Fifth', 'Al Barsha 5', 'al_barsha_5', 'Suburban', 'Dubai Municipality', 55),

-- Dubai Hills Estate
('Dubai Hills Estate', 'Dubai Hills Estate', 'dubai_hills_estate', 'Suburban', 'Dubai Municipality', 85),
('Dubai Hills Estate First', 'Dubai Hills Estate 1', 'dubai_hills_estate_1', 'Suburban', 'Dubai Municipality', 80),
('Dubai Hills Estate Second', 'Dubai Hills Estate 2', 'dubai_hills_estate_2', 'Suburban', 'Dubai Municipality', 75),

-- Arabian Ranches
('Arabian Ranches', 'Arabian Ranches', 'arabian_ranches', 'Suburban', 'Dubai Municipality', 90),
('Arabian Ranches First', 'Arabian Ranches 1', 'arabian_ranches_1', 'Suburban', 'Dubai Municipality', 85),
('Arabian Ranches Second', 'Arabian Ranches 2', 'arabian_ranches_2', 'Suburban', 'Dubai Municipality', 80),

-- Emirates Hills
('Emirates Hills', 'Emirates Hills', 'emirates_hills', 'Luxury', 'Dubai Municipality', 95),
('Emirates Hills First', 'Emirates Hills 1', 'emirates_hills_1', 'Luxury', 'Dubai Municipality', 90),
('Emirates Hills Second', 'Emirates Hills 2', 'emirates_hills_2', 'Luxury', 'Dubai Municipality', 85),

-- Jumeirah
('Jumeirah', 'Jumeirah', 'jumeirah', 'Beach', 'Dubai Municipality', 88),
('Jumeirah First', 'Jumeirah 1', 'jumeirah_1', 'Beach', 'Dubai Municipality', 85),
('Jumeirah Second', 'Jumeirah 2', 'jumeirah_2', 'Beach', 'Dubai Municipality', 82),
('Jumeirah Third', 'Jumeirah 3', 'jumeirah_3', 'Beach', 'Dubai Municipality', 80),

-- Umm Suqeim
('Umm Suqeim', 'Umm Suqeim', 'umm_suqeim', 'Beach', 'Dubai Municipality', 75),
('Umm Suqeim First', 'Umm Suqeim 1', 'umm_suqeim_1', 'Beach', 'Dubai Municipality', 70),
('Umm Suqeim Second', 'Umm Suqeim 2', 'umm_suqeim_2', 'Beach', 'Dubai Municipality', 65),
('Umm Suqeim Third', 'Umm Suqeim 3', 'umm_suqeim_3', 'Beach', 'Dubai Municipality', 60),

-- Mirdif
('Mirdif', 'Mirdif', 'mirdif', 'Suburban', 'Dubai Municipality', 70),
('Mirdif First', 'Mirdif 1', 'mirdif_1', 'Suburban', 'Dubai Municipality', 65),
('Mirdif Second', 'Mirdif 2', 'mirdif_2', 'Suburban', 'Dubai Municipality', 60),

-- International City
('International City', 'International City', 'international_city', 'Suburban', 'Dubai Municipality', 65),
('International City First', 'International City 1', 'international_city_1', 'Suburban', 'Dubai Municipality', 60),
('International City Second', 'International City 2', 'international_city_2', 'Suburban', 'Dubai Municipality', 55),

-- Silicon Oasis
('Dubai Silicon Oasis', 'Dubai Silicon Oasis', 'dubai_silicon_oasis', 'Business', 'Dubai Municipality', 75),
('Dubai Silicon Oasis First', 'Dubai Silicon Oasis 1', 'dubai_silicon_oasis_1', 'Business', 'Dubai Municipality', 70),
('Dubai Silicon Oasis Second', 'Dubai Silicon Oasis 2', 'dubai_silicon_oasis_2', 'Business', 'Dubai Municipality', 65),

-- Sports City
('Dubai Sports City', 'Dubai Sports City', 'dubai_sports_city', 'Sports', 'Dubai Municipality', 70),
('Dubai Sports City First', 'Dubai Sports City 1', 'dubai_sports_city_1', 'Sports', 'Dubai Municipality', 65),
('Dubai Sports City Second', 'Dubai Sports City 2', 'dubai_sports_city_2', 'Sports', 'Dubai Municipality', 60)

ON CONFLICT (normalized_name) DO NOTHING;

-- Now populate analytics for new areas
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
    COUNT(dt.id) as total_transactions,
    SUM(dt.price_aed) as total_volume_aed,
    AVG(dt.price_aed) as avg_price_aed,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dt.price_aed) as median_price_aed,
    MIN(dt.price_aed) as min_price_aed,
    MAX(dt.price_aed) as max_price_aed,
    AVG(dt.price_per_sqft) as price_per_sqft_avg
FROM area_mapping am
JOIN dld_transactions dt ON LOWER(dt.location) = LOWER(am.dld_area_name)
WHERE am.id NOT IN (SELECT DISTINCT area_mapping_id FROM area_analytics WHERE analysis_date = CURRENT_DATE)
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

-- Final update of area_mapping with all calculated values
UPDATE area_mapping 
SET 
    avg_price_aed = aa.avg_price_aed,
    min_price_aed = aa.min_price_aed,
    max_price_aed = aa.max_price_aed,
    transaction_volume = aa.total_transactions,
    last_updated = CURRENT_TIMESTAMP
FROM area_analytics aa
WHERE aa.area_mapping_id = area_mapping.id
AND aa.analysis_date = CURRENT_DATE;

-- Update popularity scores based on transaction volume
UPDATE area_mapping 
SET popularity_score = CASE
    WHEN transaction_volume > 1000 THEN 100
    WHEN transaction_volume > 500 THEN 80
    WHEN transaction_volume > 100 THEN 60
    WHEN transaction_volume > 50 THEN 40
    WHEN transaction_volume > 10 THEN 20
    ELSE 10
END;
