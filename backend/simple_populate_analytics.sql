-- Simple script to populate area analytics
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
    COALESCE(COUNT(dt.id), 0) as total_transactions,
    COALESCE(SUM(dt.price_aed), 0) as total_volume_aed,
    COALESCE(AVG(dt.price_aed), 0) as avg_price_aed,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dt.price_aed), 0) as median_price_aed,
    COALESCE(MIN(dt.price_aed), 0) as min_price_aed,
    COALESCE(MAX(dt.price_aed), 0) as max_price_aed,
    COALESCE(AVG(dt.price_per_sqft), 0) as price_per_sqft_avg
FROM area_mapping am
LEFT JOIN dld_transactions dt ON LOWER(dt.location) = LOWER(am.dld_area_name)
GROUP BY am.id;

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

-- Update popularity scores
UPDATE area_mapping 
SET popularity_score = CASE
    WHEN transaction_volume > 1000 THEN 100
    WHEN transaction_volume > 500 THEN 80
    WHEN transaction_volume > 100 THEN 60
    WHEN transaction_volume > 50 THEN 40
    WHEN transaction_volume > 10 THEN 20
    ELSE 10
END;

