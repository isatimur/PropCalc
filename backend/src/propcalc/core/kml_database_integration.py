"""
Database integration for KML data storage and retrieval
Handles geographic areas, points, and lines for area searches and mapping
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.extensions import connection

logger = logging.getLogger(__name__)

class KMLDatabaseIntegration:
    """Handles database operations for KML data"""
    
    def __init__(self, db_connection: connection):
        self.db = db_connection
    
    def create_tables(self):
        """Create the necessary tables for KML data"""
        try:
            with self.db.cursor() as cursor:
                # Create geographic areas table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS geographic_areas (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255),
                        name_arabic VARCHAR(255),
                        name_english VARCHAR(255),
                        sector_number VARCHAR(50),
                        community_number VARCHAR(50),
                        dgis_id VARCHAR(50),
                        ndgis_id VARCHAR(50),
                        center_latitude DECIMAL(10,8),
                        center_longitude DECIMAL(11,8),
                        area_sqm DECIMAL(15,2),
                        perimeter_m DECIMAL(15,2),
                        polygon_coordinates TEXT,
                        properties JSONB,
                        source_file VARCHAR(255),
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Create geographic points table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS geographic_points (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255),
                        latitude DECIMAL(10,8),
                        longitude DECIMAL(11,8),
                        altitude DECIMAL(10,3),
                        properties JSONB,
                        source_file VARCHAR(255),
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Create geographic lines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS geographic_lines (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255),
                        coordinates TEXT,
                        properties JSONB,
                        source_file VARCHAR(255),
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Create indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_areas_sector 
                    ON geographic_areas(sector_number);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_areas_community 
                    ON geographic_areas(community_number);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_areas_center 
                    ON geographic_areas(center_latitude, center_longitude);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_areas_name 
                    ON geographic_areas(name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_points_coords 
                    ON geographic_points(latitude, longitude);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_points_name 
                    ON geographic_points(name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_geographic_lines_name 
                    ON geographic_lines(name);
                """)
                
                self.db.commit()
                logger.info("KML database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating KML database tables: {e}")
            self.db.rollback()
            raise
    
    def insert_area_data(self, area_data: Dict[str, Any]) -> bool:
        """Insert area data into database"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO geographic_areas (
                        id, name, name_arabic, name_english, sector_number,
                        community_number, dgis_id, ndgis_id, center_latitude,
                        center_longitude, area_sqm, perimeter_m, polygon_coordinates,
                        properties, source_file
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        name_arabic = EXCLUDED.name_arabic,
                        name_english = EXCLUDED.name_english,
                        sector_number = EXCLUDED.sector_number,
                        community_number = EXCLUDED.community_number,
                        dgis_id = EXCLUDED.dgis_id,
                        ndgis_id = EXCLUDED.ndgis_id,
                        center_latitude = EXCLUDED.center_latitude,
                        center_longitude = EXCLUDED.center_longitude,
                        area_sqm = EXCLUDED.area_sqm,
                        perimeter_m = EXCLUDED.perimeter_m,
                        polygon_coordinates = EXCLUDED.polygon_coordinates,
                        properties = EXCLUDED.properties,
                        source_file = EXCLUDED.source_file
                    """, (
                        area_data.get('id'),
                        area_data.get('name'),
                        area_data.get('name_arabic'),
                        area_data.get('name_english'),
                        area_data.get('sector_number'),
                        area_data.get('community_number'),
                        area_data.get('dgis_id'),
                        area_data.get('ndgis_id'),
                        area_data.get('center_latitude'),
                        area_data.get('center_longitude'),
                        area_data.get('area_sqm'),
                        area_data.get('perimeter_m'),
                        json.dumps(area_data.get('polygon_coordinates', [])),
                        Json(area_data.get('properties', {})),
                        area_data.get('source_file')
                    ))
                
                return True
                
        except Exception as e:
            logger.error(f"Error inserting area data: {e}")
            return False
    
    def insert_point_data(self, point_data: Dict[str, Any]) -> bool:
        """Insert point data into database"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO geographic_points (
                        id, name, latitude, longitude, altitude,
                        properties, source_file
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        altitude = EXCLUDED.altitude,
                        properties = EXCLUDED.properties,
                        source_file = EXCLUDED.source_file
                    """, (
                        point_data.get('id'),
                        point_data.get('name'),
                        point_data.get('latitude'),
                        point_data.get('longitude'),
                        point_data.get('altitude'),
                        Json(point_data.get('properties', {})),
                        point_data.get('source_file')
                    ))
                
                return True
                
        except Exception as e:
            logger.error(f"Error inserting point data: {e}")
            return False
    
    def insert_line_data(self, line_data: Dict[str, Any]) -> bool:
        """Insert line data into database"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO geographic_lines (
                        id, name, coordinates, properties, source_file
                    ) VALUES (
                        %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        coordinates = EXCLUDED.coordinates,
                        properties = EXCLUDED.properties,
                        source_file = EXCLUDED.source_file
                    """, (
                        line_data.get('id'),
                        line_data.get('name'),
                        json.dumps(line_data.get('coordinates', [])),
                        Json(line_data.get('properties', {})),
                        line_data.get('source_file')
                    ))
                
                return True
                
        except Exception as e:
            logger.error(f"Error inserting line data: {e}")
            return False
    
    def search_areas_by_name(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search areas by name (English or Arabic)"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM geographic_areas 
                    WHERE name ILIKE %s 
                       OR name_english ILIKE %s 
                       OR name_arabic ILIKE %s
                    ORDER BY name
                    LIMIT %s
                """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error searching areas by name: {e}")
            return []
    
    def search_areas_by_sector(self, sector_number: str) -> List[Dict[str, Any]]:
        """Search areas by sector number"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM geographic_areas 
                    WHERE sector_number = %s
                    ORDER BY name
                """, (sector_number,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error searching areas by sector: {e}")
            return []
    
    def search_areas_by_community(self, community_number: str) -> List[Dict[str, Any]]:
        """Search areas by community number"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM geographic_areas 
                    WHERE community_number = %s
                    ORDER BY name
                """, (community_number,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error searching areas by community: {e}")
            return []
    
    def find_areas_near_coordinates(self, lat: float, lon: float, radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """Find areas near given coordinates"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT *, 
                           (6371 * acos(
                               cos(radians(%s)) * 
                               cos(radians(center_latitude)) * 
                               cos(radians(center_longitude) - radians(%s)) + 
                               sin(radians(%s)) * 
                               sin(radians(center_latitude))
                           )) as distance_km
                    FROM geographic_areas
                    WHERE (6371 * acos(
                        cos(radians(%s)) * 
                        cos(radians(center_latitude)) * 
                        cos(radians(center_longitude) - radians(%s)) + 
                        sin(radians(%s)) * 
                        sin(radians(center_latitude))
                    )) <= %s
                    ORDER BY distance_km
                """, (lat, lon, lat, lat, lon, lat, radius_km))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error finding areas near coordinates: {e}")
            return []
    
    def find_points_near_coordinates(self, lat: float, lon: float, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Find points near given coordinates"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT *, 
                           (6371 * acos(
                               cos(radians(%s)) * 
                               cos(radians(latitude)) * 
                               cos(radians(longitude) - radians(%s)) + 
                               sin(radians(%s)) * 
                               sin(radians(latitude))
                           )) as distance_km
                    FROM geographic_points
                    WHERE (6371 * acos(
                        cos(radians(%s)) * 
                        cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(%s)) + 
                        sin(radians(%s)) * 
                        sin(radians(latitude))
                    )) <= %s
                    ORDER BY distance_km
                """, (lat, lon, lat, lat, lon, lat, radius_km))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error finding points near coordinates: {e}")
            return []
    
    def get_area_by_id(self, area_id: int) -> Optional[Dict[str, Any]]:
        """Get area by ID"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM geographic_areas WHERE id = %s
                """, (area_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting area by ID: {e}")
            return None
    
    def get_point_by_id(self, point_id: int) -> Optional[Dict[str, Any]]:
        """Get point by ID"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM geographic_points WHERE id = %s
                """, (point_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting point by ID: {e}")
            return None
    
    def get_all_sectors(self) -> List[Dict[str, Any]]:
        """Get all unique sectors"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT sector_number, 
                           COUNT(*) as area_count,
                           MIN(name) as sample_name
                    FROM geographic_areas 
                    WHERE sector_number IS NOT NULL AND sector_number != ''
                    GROUP BY sector_number
                    ORDER BY sector_number
                """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting sectors: {e}")
            return []
    
    def get_all_communities(self) -> List[Dict[str, Any]]:
        """Get all unique communities"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT community_number,
                           COUNT(*) as area_count,
                           MIN(name) as sample_name
                    FROM geographic_areas 
                    WHERE community_number IS NOT NULL AND community_number != ''
                    GROUP BY community_number
                    ORDER BY community_number
                """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting communities: {e}")
            return []
    
    def get_area_statistics(self) -> Dict[str, Any]:
        """Get statistics about geographic areas"""
        try:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                # Total areas
                cursor.execute("SELECT COUNT(*) as total_areas FROM geographic_areas")
                total_areas = cursor.fetchone()['total_areas']
                
                # Total points
                cursor.execute("SELECT COUNT(*) as total_points FROM geographic_points")
                total_points = cursor.fetchone()['total_points']
                
                # Total lines
                cursor.execute("SELECT COUNT(*) as total_lines FROM geographic_lines")
                total_lines = cursor.fetchone()['total_lines']
                
                # Average area size
                cursor.execute("""
                    SELECT AVG(area_sqm) as avg_area_sqm,
                           MAX(area_sqm) as max_area_sqm,
                           MIN(area_sqm) as min_area_sqm
                    FROM geographic_areas 
                    WHERE area_sqm > 0
                """)
                area_stats = cursor.fetchone()
                
                # Source files
                cursor.execute("""
                    SELECT source_file, COUNT(*) as count
                    FROM geographic_areas
                    GROUP BY source_file
                    ORDER BY count DESC
                """)
                source_files = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'total_areas': total_areas,
                    'total_points': total_points,
                    'total_lines': total_lines,
                    'area_statistics': dict(area_stats) if area_stats else {},
                    'source_files': source_files
                }
                
        except Exception as e:
            logger.error(f"Error getting area statistics: {e}")
            return {}
    
    def bulk_insert_areas(self, areas: List[Dict[str, Any]]) -> int:
        """Bulk insert area data"""
        try:
            with self.db.cursor() as cursor:
                inserted_count = 0
                
                for area in areas:
                    if self.insert_area_data(area):
                        inserted_count += 1
                
                self.db.commit()
                logger.info(f"Bulk inserted {inserted_count} areas")
                return inserted_count
                
        except Exception as e:
            logger.error(f"Error bulk inserting areas: {e}")
            self.db.rollback()
            return 0
    
    def bulk_insert_points(self, points: List[Dict[str, Any]]) -> int:
        """Bulk insert point data"""
        try:
            with self.db.cursor() as cursor:
                inserted_count = 0
                
                for point in points:
                    if self.insert_point_data(point):
                        inserted_count += 1
                
                self.db.commit()
                logger.info(f"Bulk inserted {inserted_count} points")
                return inserted_count
                
        except Exception as e:
            logger.error(f"Error bulk inserting points: {e}")
            self.db.rollback()
            return 0
    
    def bulk_insert_lines(self, lines: List[Dict[str, Any]]) -> int:
        """Bulk insert line data"""
        try:
            with self.db.cursor() as cursor:
                inserted_count = 0
                
                for line in lines:
                    if self.insert_line_data(line):
                        inserted_count += 1
                
                self.db.commit()
                logger.info(f"Bulk inserted {inserted_count} lines")
                return inserted_count
                
        except Exception as e:
            logger.error(f"Error bulk inserting lines: {e}")
            self.db.rollback()
            return 0
    
    def clear_all_data(self):
        """Clear all KML data from database"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM geographic_areas")
                cursor.execute("DELETE FROM geographic_points")
                cursor.execute("DELETE FROM geographic_lines")
                
                self.db.commit()
                logger.info("Cleared all KML data from database")
                
        except Exception as e:
            logger.error(f"Error clearing KML data: {e}")
            self.db.rollback()
            raise 