#!/usr/bin/env python3
"""
Script to load processed KML data into the database
"""

import os
import sys
import json
import logging
import csv
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from propcalc.core.kml_database_integration import KMLDatabaseIntegration
import psycopg2
import os

def get_db_connection():
    """Get a synchronous database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        user=os.getenv('POSTGRES_USER', 'vantage_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'vantage_password'),
        database=os.getenv('POSTGRES_DB', 'vantage_ai')
    )

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('kml_database_loading.log'),
            logging.StreamHandler()
        ]
    )

def load_csv_data(csv_file: Path, kml_db: KMLDatabaseIntegration, data_type: str):
    """Load CSV data into database"""
    logger = logging.getLogger(__name__)
    
    try:
        if data_type == 'areas':
            areas = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string values to appropriate types
                    area_data = {
                        'id': int(row['id']) if row['id'] else 0,
                        'name': row['name'] or '',
                        'name_arabic': row['name_arabic'] or None,
                        'name_english': row['name_english'] or None,
                        'sector_number': row['sector_number'] or None,
                        'community_number': row['community_number'] or None,
                        'dgis_id': row['dgis_id'] or None,
                        'ndgis_id': row['ndgis_id'] or None,
                        'center_latitude': float(row['center_latitude']) if row['center_latitude'] else None,
                        'center_longitude': float(row['center_longitude']) if row['center_longitude'] else None,
                        'area_sqm': float(row['area_sqm']) if row['area_sqm'] else None,
                        'perimeter_m': float(row['perimeter_m']) if row['perimeter_m'] else None,
                        'source_file': csv_file.name,
                        'properties': {},
                        'polygon_coordinates': []
                    }
                    areas.append(area_data)
            
            inserted_count = kml_db.bulk_insert_areas(areas)
            logger.info(f"Loaded {inserted_count} areas from {csv_file.name}")
            return inserted_count
            
        elif data_type == 'points':
            points = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    point_data = {
                        'id': int(row['id']) if row['id'] else 0,
                        'name': row['name'] or '',
                        'latitude': float(row['latitude']) if row['latitude'] else 0.0,
                        'longitude': float(row['longitude']) if row['longitude'] else 0.0,
                        'altitude': float(row['altitude']) if row['altitude'] else 0.0,
                        'source_file': csv_file.name,
                        'properties': {}
                    }
                    points.append(point_data)
            
            inserted_count = kml_db.bulk_insert_points(points)
            logger.info(f"Loaded {inserted_count} points from {csv_file.name}")
            return inserted_count
            
    except Exception as e:
        logger.error(f"Error loading {data_type} from {csv_file}: {e}")
        return 0

def main():
    """Main function to load KML data into database"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get the processed data directory
    script_dir = Path(__file__).parent
    processed_data_dir = script_dir / 'processed_kml_data'
    csv_dir = processed_data_dir / 'csv'
    
    if not csv_dir.exists():
        logger.error(f"CSV directory not found: {csv_dir}")
        return
    
    # Initialize database connection
    try:
        db_connection = get_db_connection()
        kml_db = KMLDatabaseIntegration(db_connection)
        
        # Create tables
        logger.info("Creating KML database tables...")
        kml_db.create_tables()
        
        # Clear existing data
        logger.info("Clearing existing KML data...")
        kml_db.clear_all_data()
        
        # Load areas
        total_areas = 0
        total_points = 0
        
        for csv_file in csv_dir.glob("*.csv"):
            if "areas" in csv_file.name:
                count = load_csv_data(csv_file, kml_db, 'areas')
                total_areas += count
            elif "points" in csv_file.name:
                count = load_csv_data(csv_file, kml_db, 'points')
                total_points += count
        
        # Get statistics
        stats = kml_db.get_area_statistics()
        
        print("\n" + "="*50)
        print("KML DATABASE LOADING SUMMARY")
        print("="*50)
        print(f"Total areas loaded: {total_areas}")
        print(f"Total points loaded: {total_points}")
        print(f"Database statistics: {stats}")
        
        # Test some queries
        print("\n" + "="*50)
        print("TESTING QUERIES")
        print("="*50)
        
        # Test area search
        test_areas = kml_db.search_areas_by_name("Dubai", 5)
        print(f"Areas with 'Dubai' in name: {len(test_areas)}")
        for area in test_areas[:3]:
            print(f"  - {area.get('name')} ({area.get('name_english')})")
        
        # Test sector search
        sectors = kml_db.get_all_sectors()
        print(f"\nTotal sectors: {len(sectors)}")
        for sector in sectors[:5]:
            print(f"  - Sector {sector.get('sector_number')}: {sector.get('area_count')} areas")
        
        # Test community search
        communities = kml_db.get_all_communities()
        print(f"\nTotal communities: {len(communities)}")
        for community in communities[:5]:
            print(f"  - Community {community.get('community_number')}: {community.get('area_count')} areas")
        
        # Test coordinate search
        test_coords = kml_db.find_areas_near_coordinates(25.2048, 55.2708, 5.0)  # Dubai coordinates
        print(f"\nAreas near Dubai center (5km radius): {len(test_coords)}")
        for area in test_coords[:3]:
            print(f"  - {area.get('name')} ({area.get('distance_km', 0):.2f}km away)")
        
        db_connection.close()
        
    except Exception as e:
        logger.error(f"Error loading KML data to database: {e}")
        raise

if __name__ == "__main__":
    main() 