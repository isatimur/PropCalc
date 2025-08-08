"""
DLD-KML Integration System
Connects DLD area data with KML geographic data for location-based real estate analysis
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.extensions import connection

logger = logging.getLogger(__name__)

@dataclass
class DLDArea:
    """DLD Area data model"""
    area_id: int
    name_en: str
    name_ar: str
    municipality_number: str

@dataclass
class GeographicArea:
    """Geographic area from KML data"""
    id: int
    name: str
    name_arabic: Optional[str]
    name_english: Optional[str]
    center_latitude: Optional[float]
    center_longitude: Optional[float]
    area_sqm: Optional[float]
    perimeter_m: Optional[float]
    polygon_coordinates: List[Tuple[float, float, float]]

@dataclass
class AreaMatch:
    """Represents a match between DLD and KML areas"""
    dld_area: DLDArea
    geographic_area: GeographicArea
    confidence_score: float
    match_type: str  # 'exact', 'fuzzy', 'coordinate_based'

class DLDKMLIntegration:
    """Integrates DLD area data with KML geographic data"""
    
    def __init__(self, db_connection: connection):
        self.db = db_connection
    
    def create_integration_tables(self):
        """Create tables for DLD-KML integration"""
        try:
            with self.db.cursor() as cursor:
                # Create area mapping table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dld_kml_area_mapping (
                        id SERIAL PRIMARY KEY,
                        dld_area_id INTEGER REFERENCES dld_areas(area_id),
                        geographic_area_id INTEGER REFERENCES geographic_areas(id),
                        confidence_score DECIMAL(3,2),
                        match_type VARCHAR(50),
                        match_criteria JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(dld_area_id, geographic_area_id)
                    );
                """)
                
                # Create area statistics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS area_market_statistics (
                        id SERIAL PRIMARY KEY,
                        area_id INTEGER REFERENCES dld_areas(area_id) UNIQUE,
                        geographic_area_id INTEGER REFERENCES geographic_areas(id),
                        total_transactions INTEGER DEFAULT 0,
                        avg_price_aed DECIMAL(15,2),
                        avg_price_per_sqft DECIMAL(10,2),
                        total_volume_aed DECIMAL(20,2),
                        property_types JSONB,
                        transaction_types JSONB,
                        last_updated TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Create indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_dld_kml_mapping_dld_area 
                    ON dld_kml_area_mapping(dld_area_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_dld_kml_mapping_geo_area 
                    ON dld_kml_area_mapping(geographic_area_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_area_market_stats_area 
                    ON area_market_statistics(area_id);
                """)
                
                self.db.commit()
                logger.info("DLD-KML integration tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating DLD-KML integration tables: {e}")
            self.db.rollback()
            raise
    
    def get_dld_areas(self) -> List[DLDArea]:
        """Get all DLD areas"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT area_id, name_en, name_ar, municipality_number
                    FROM dld_areas
                    ORDER BY name_en
                """)
                
                areas = []
                for row in cursor.fetchall():
                    areas.append(DLDArea(
                        area_id=row['area_id'],
                        name_en=row['name_en'],
                        name_ar=row['name_ar'],
                        municipality_number=row['municipality_number']
                    ))
                
                return areas
                
        except Exception as e:
            logger.error(f"Error getting DLD areas: {e}")
            return []
    
    def get_geographic_areas(self) -> List[GeographicArea]:
        """Get all geographic areas from KML data"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, name, name_arabic, name_english, 
                           center_latitude, center_longitude, area_sqm, perimeter_m,
                           polygon_coordinates
                    FROM geographic_areas
                    ORDER BY name
                """)
                
                areas = []
                for row in cursor.fetchall():
                    # Parse polygon coordinates
                    import json
                    polygon_coords = json.loads(row.get('polygon_coordinates', '[]'))
                    
                    areas.append(GeographicArea(
                        id=row['id'],
                        name=row['name'],
                        name_arabic=row['name_arabic'],
                        name_english=row['name_english'],
                        center_latitude=row['center_latitude'],
                        center_longitude=row['center_longitude'],
                        area_sqm=row['area_sqm'],
                        perimeter_m=row['perimeter_m'],
                        polygon_coordinates=polygon_coords
                    ))
                
                return areas
                
        except Exception as e:
            logger.error(f"Error getting geographic areas: {e}")
            return []
    
    def find_area_matches(self) -> List[AreaMatch]:
        """Find matches between DLD areas and KML geographic areas"""
        dld_areas = self.get_dld_areas()
        geographic_areas = self.get_geographic_areas()
        
        matches = []
        
        for dld_area in dld_areas:
            for geo_area in geographic_areas:
                match = self._calculate_area_match(dld_area, geo_area)
                if match and match.confidence_score > 0.3:  # Minimum confidence threshold
                    matches.append(match)
        
        return matches
    
    def _calculate_area_match(self, dld_area: DLDArea, geo_area: GeographicArea) -> Optional[AreaMatch]:
        """Calculate match confidence between DLD and geographic areas"""
        
        # 1. Exact name match (highest confidence)
        if self._exact_name_match(dld_area, geo_area):
            return AreaMatch(
                dld_area=dld_area,
                geographic_area=geo_area,
                confidence_score=1.0,
                match_type='exact'
            )
        
        # 2. Fuzzy name match
        fuzzy_score = self._fuzzy_name_match(dld_area, geo_area)
        if fuzzy_score > 0.8:
            return AreaMatch(
                dld_area=dld_area,
                geographic_area=geo_area,
                confidence_score=fuzzy_score,
                match_type='fuzzy'
            )
        
        # 3. Partial name match
        partial_score = self._partial_name_match(dld_area, geo_area)
        if partial_score > 0.6:
            return AreaMatch(
                dld_area=dld_area,
                geographic_area=geo_area,
                confidence_score=partial_score,
                match_type='partial'
            )
        
        return None
    
    def _exact_name_match(self, dld_area: DLDArea, geo_area: GeographicArea) -> bool:
        """Check for exact name match"""
        dld_name = dld_area.name_en.lower().strip()
        geo_name = geo_area.name_english.lower().strip() if geo_area.name_english else ""
        
        return dld_name == geo_name
    
    def _fuzzy_name_match(self, dld_area: DLDArea, geo_area: GeographicArea) -> float:
        """Calculate fuzzy name match score"""
        from difflib import SequenceMatcher
        
        dld_name = dld_area.name_en.lower().strip()
        geo_name = geo_area.name_english.lower().strip() if geo_area.name_english else ""
        
        if not geo_name:
            return 0.0
        
        # Use sequence matcher for fuzzy matching
        similarity = SequenceMatcher(None, dld_name, geo_name).ratio()
        return similarity
    
    def _partial_name_match(self, dld_area: DLDArea, geo_area: GeographicArea) -> float:
        """Calculate partial name match score"""
        dld_name = dld_area.name_en.lower().strip()
        geo_name = geo_area.name_english.lower().strip() if geo_area.name_english else ""
        
        if not geo_name:
            return 0.0
        
        # Check if one name contains the other
        if dld_name in geo_name or geo_name in dld_name:
            return 0.7
        
        # Check for common words
        dld_words = set(dld_name.split())
        geo_words = set(geo_name.split())
        
        if dld_words and geo_words:
            common_words = dld_words.intersection(geo_words)
            if common_words:
                return len(common_words) / max(len(dld_words), len(geo_words))
        
        return 0.0
    
    def save_area_matches(self, matches: List[AreaMatch]):
        """Save area matches to database"""
        try:
            with self.db.cursor() as cursor:
                for match in matches:
                    cursor.execute("""
                        INSERT INTO dld_kml_area_mapping (
                            dld_area_id, geographic_area_id, confidence_score, 
                            match_type, match_criteria, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT (dld_area_id, geographic_area_id) DO UPDATE SET
                            confidence_score = EXCLUDED.confidence_score,
                            match_type = EXCLUDED.match_type,
                            match_criteria = EXCLUDED.match_criteria,
                            updated_at = EXCLUDED.updated_at
                    """, (
                        match.dld_area.area_id,
                        match.geographic_area.id,
                        match.confidence_score,
                        match.match_type,
                        Json({
                            'dld_name': match.dld_area.name_en,
                            'geo_name': match.geographic_area.name_english,
                            'match_score': match.confidence_score
                        }),
                        datetime.now()
                    ))
                
                self.db.commit()
                logger.info(f"Saved {len(matches)} area matches to database")
                
        except Exception as e:
            logger.error(f"Error saving area matches: {e}")
            self.db.rollback()
            raise
    
    def get_area_market_statistics(self, area_id: int) -> Dict[str, Any]:
        """Get market statistics for a specific area"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get basic area info
                cursor.execute("""
                    SELECT da.area_id, da.name_en, da.name_ar,
                           ga.center_latitude, ga.center_longitude,
                           ga.area_sqm, ga.perimeter_m
                    FROM dld_areas da
                    LEFT JOIN dld_kml_area_mapping dkam ON da.area_id = dkam.dld_area_id
                    LEFT JOIN geographic_areas ga ON dkam.geographic_area_id = ga.id
                    WHERE da.area_id = %s
                """, (area_id,))
                
                area_info = cursor.fetchone()
                if not area_info:
                    return {}
                
                # Get transaction statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_transactions,
                        AVG(price_aed) as avg_price_aed,
                        AVG(CASE WHEN area_sqft > 0 THEN price_aed / area_sqft ELSE NULL END) as avg_price_per_sqft,
                        SUM(price_aed) as total_volume_aed,
                        COUNT(DISTINCT property_type) as property_type_count
                    FROM dld_transactions
                    WHERE area_id = %s
                    AND price_aed > 0
                """, (area_id,))
                
                transaction_stats = cursor.fetchone()
                
                # Get property type distribution
                cursor.execute("""
                    SELECT property_type, COUNT(*) as count
                    FROM dld_transactions
                    WHERE area_id = %s
                    GROUP BY property_type
                    ORDER BY count DESC
                """, (area_id,))
                
                property_types = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'area_info': dict(area_info) if area_info else {},
                    'transaction_stats': dict(transaction_stats) if transaction_stats else {},
                    'property_types': property_types
                }
                
        except Exception as e:
            logger.error(f"Error getting area market statistics: {e}")
            return {}
    
    def search_areas_by_location(self, lat: float, lon: float, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Search areas by coordinates with market data"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        da.area_id, da.name_en, da.name_ar,
                        ga.center_latitude, ga.center_longitude,
                        ga.area_sqm, ga.perimeter_m,
                        (6371 * acos(
                            cos(radians(%s)) * 
                            cos(radians(ga.center_latitude)) * 
                            cos(radians(ga.center_longitude) - radians(%s)) + 
                            sin(radians(%s)) * 
                            sin(radians(ga.center_latitude))
                        )) as distance_km
                    FROM dld_areas da
                    JOIN dld_kml_area_mapping dkam ON da.area_id = dkam.dld_area_id
                    JOIN geographic_areas ga ON dkam.geographic_area_id = ga.id
                    WHERE (6371 * acos(
                        cos(radians(%s)) * 
                        cos(radians(ga.center_latitude)) * 
                        cos(radians(ga.center_longitude) - radians(%s)) + 
                        sin(radians(%s)) * 
                        sin(radians(ga.center_latitude))
                    )) <= %s
                    ORDER BY distance_km
                """, (lat, lon, lat, lat, lon, lat, radius_km))
                
                areas = [dict(row) for row in cursor.fetchall()]
                
                # Add market statistics for each area
                for area in areas:
                    stats = self.get_area_market_statistics(area['area_id'])
                    area['market_statistics'] = stats
                
                return areas
                
        except Exception as e:
            logger.error(f"Error searching areas by location: {e}")
            return []
    
    def get_area_transactions(self, area_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent transactions for an area"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                                                    transaction_id, property_type, location,
                            transaction_date, price_aed, area_sqft,
                            developer_name, project_name
                    FROM dld_transactions
                    WHERE area_id = %s
                    ORDER BY instance_date DESC
                    LIMIT %s
                """, (area_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting area transactions: {e}")
            return []
    
    def get_area_geographic_data(self, area_id: int) -> Optional[Dict[str, Any]]:
        """Get geographic data for a DLD area"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        ga.id, ga.name, ga.name_arabic, ga.name_english,
                        ga.center_latitude, ga.center_longitude,
                        ga.area_sqm, ga.perimeter_m, ga.polygon_coordinates,
                        dkam.confidence_score, dkam.match_type
                    FROM dld_areas da
                    JOIN dld_kml_area_mapping dkam ON da.area_id = dkam.dld_area_id
                    JOIN geographic_areas ga ON dkam.geographic_area_id = ga.id
                    WHERE da.area_id = %s
                    ORDER BY dkam.confidence_score DESC
                    LIMIT 1
                """, (area_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting area geographic data: {e}")
            return None
    
    def update_area_market_statistics(self):
        """Update market statistics for all areas"""
        try:
            with self.db.cursor() as cursor:
                # Get all areas with transactions
                cursor.execute("""
                    SELECT DISTINCT area_id FROM dld_transactions
                    WHERE area_id IS NOT NULL
                """)
                
                area_ids = [row[0] for row in cursor.fetchall()]
                
                for area_id in area_ids:
                    # Calculate basic statistics
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_transactions,
                            AVG(price_aed) as avg_price_aed,
                            AVG(CASE WHEN area_sqft > 0 THEN price_aed / area_sqft ELSE NULL END) as avg_price_per_sqft,
                            SUM(price_aed) as total_volume_aed
                        FROM dld_transactions
                        WHERE area_id = %s AND price_aed > 0
                    """, (area_id,))
                    
                    stats = cursor.fetchone()
                    if stats and stats[0] > 0:  # Only insert if there are transactions
                        # Get property type distribution
                        cursor.execute("""
                            SELECT property_type, COUNT(*) as count
                            FROM dld_transactions
                            WHERE area_id = %s
                            GROUP BY property_type
                        """, (area_id,))
                        
                        property_types = {row[0]: row[1] for row in cursor.fetchall()}
                        
                        # Delete existing record if exists
                        cursor.execute("DELETE FROM area_market_statistics WHERE area_id = %s", (area_id,))
                        
                        # Insert new statistics
                        cursor.execute("""
                            INSERT INTO area_market_statistics (
                                area_id, total_transactions, avg_price_aed,
                                avg_price_per_sqft, total_volume_aed,
                                property_types, transaction_types, last_updated
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (
                            area_id, stats[0], stats[1], stats[2], stats[3],
                            Json(property_types), Json({})
                        ))
                
                self.db.commit()
                logger.info(f"Updated market statistics for {len(area_ids)} areas")
                
        except Exception as e:
            logger.error(f"Error updating area market statistics: {e}")
            self.db.rollback()
            raise 