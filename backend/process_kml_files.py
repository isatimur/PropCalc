#!/usr/bin/env python3
"""
Script to process KML files and transform them into database-friendly formats
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from propcalc.core.kml_processor import KMLProcessor

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('kml_processing.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main function to process KML files"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get the data directory path
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return
    
    # Create output directories
    output_dir = script_dir / 'processed_kml_data'
    output_dir.mkdir(exist_ok=True)
    
    csv_output_dir = output_dir / 'csv'
    csv_output_dir.mkdir(exist_ok=True)
    
    json_output_dir = output_dir / 'json'
    json_output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Processing KML files from: {data_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Initialize KML processor
    processor = KMLProcessor()
    
    try:
        # Process all KML files
        results = processor.process_all_kml_files(str(data_dir))
        
        # Export to JSON
        json_file = json_output_dir / 'kml_processed_data.json'
        processor.export_to_json(results, str(json_file))
        
        # Export to CSV
        processor.export_to_csv(results, str(csv_output_dir))
        
        # Print summary
        print("\n" + "="*50)
        print("KML PROCESSING SUMMARY")
        print("="*50)
        
        total_areas = 0
        total_points = 0
        total_lines = 0
        
        for file_name, file_data in results.items():
            if isinstance(file_data, dict) and 'error' not in file_data:
                areas_count = len(file_data.get('areas', []))
                points_count = len(file_data.get('points', []))
                lines_count = len(file_data.get('lines', []))
                
                total_areas += areas_count
                total_points += points_count
                total_lines += lines_count
                
                print(f"\n{file_name}:")
                print(f"  - Areas (Polygons): {areas_count}")
                print(f"  - Points: {points_count}")
                print(f"  - Lines: {lines_count}")
            else:
                print(f"\n{file_name}: ERROR - {file_data.get('error', 'Unknown error')}")
        
        print(f"\nTOTALS:")
        print(f"  - Total Areas: {total_areas}")
        print(f"  - Total Points: {total_points}")
        print(f"  - Total Lines: {total_lines}")
        print(f"\nOutput files:")
        print(f"  - JSON: {json_file}")
        print(f"  - CSV files: {csv_output_dir}")
        
        # Create database schema suggestions
        create_database_schema_suggestions(results, output_dir)
        
    except Exception as e:
        logger.error(f"Error processing KML files: {e}")
        raise

def create_database_schema_suggestions(results: dict, output_dir: Path):
    """Create database schema suggestions based on processed data"""
    logger = logging.getLogger(__name__)
    
    schema_suggestions = {
        "tables": {
            "geographic_areas": {
                "description": "Stores polygon areas from KML files (sectors, communities)",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY", "description": "Unique identifier"},
                    {"name": "name", "type": "VARCHAR(255)", "description": "Area name"},
                    {"name": "name_arabic", "type": "VARCHAR(255)", "description": "Arabic name"},
                    {"name": "name_english", "type": "VARCHAR(255)", "description": "English name"},
                    {"name": "sector_number", "type": "VARCHAR(50)", "description": "Sector number"},
                    {"name": "community_number", "type": "VARCHAR(50)", "description": "Community number"},
                    {"name": "dgis_id", "type": "VARCHAR(50)", "description": "DGIS identifier"},
                    {"name": "ndgis_id", "type": "VARCHAR(50)", "description": "NDGIS identifier"},
                    {"name": "center_latitude", "type": "DECIMAL(10,8)", "description": "Center latitude"},
                    {"name": "center_longitude", "type": "DECIMAL(11,8)", "description": "Center longitude"},
                    {"name": "area_sqm", "type": "DECIMAL(15,2)", "description": "Area in square meters"},
                    {"name": "perimeter_m", "type": "DECIMAL(15,2)", "description": "Perimeter in meters"},
                    {"name": "polygon_coordinates", "type": "TEXT", "description": "JSON array of polygon coordinates"},
                    {"name": "properties", "type": "JSONB", "description": "Additional properties from KML"},
                    {"name": "source_file", "type": "VARCHAR(255)", "description": "Source KML file"},
                    {"name": "created_at", "type": "TIMESTAMP DEFAULT NOW()", "description": "Record creation time"}
                ],
                "indexes": [
                    "CREATE INDEX idx_geographic_areas_sector ON geographic_areas(sector_number);",
                    "CREATE INDEX idx_geographic_areas_community ON geographic_areas(community_number);",
                    "CREATE INDEX idx_geographic_areas_center ON geographic_areas(center_latitude, center_longitude);",
                    "CREATE INDEX idx_geographic_areas_name ON geographic_areas(name);"
                ]
            },
            "geographic_points": {
                "description": "Stores point data from KML files (entrances, landmarks)",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY", "description": "Unique identifier"},
                    {"name": "name", "type": "VARCHAR(255)", "description": "Point name"},
                    {"name": "latitude", "type": "DECIMAL(10,8)", "description": "Latitude"},
                    {"name": "longitude", "type": "DECIMAL(11,8)", "description": "Longitude"},
                    {"name": "altitude", "type": "DECIMAL(10,3)", "description": "Altitude"},
                    {"name": "properties", "type": "JSONB", "description": "Additional properties from KML"},
                    {"name": "source_file", "type": "VARCHAR(255)", "description": "Source KML file"},
                    {"name": "created_at", "type": "TIMESTAMP DEFAULT NOW()", "description": "Record creation time"}
                ],
                "indexes": [
                    "CREATE INDEX idx_geographic_points_coords ON geographic_points(latitude, longitude);",
                    "CREATE INDEX idx_geographic_points_name ON geographic_points(name);"
                ]
            },
            "geographic_lines": {
                "description": "Stores line data from KML files (roads, boundaries)",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY", "description": "Unique identifier"},
                    {"name": "name", "type": "VARCHAR(255)", "description": "Line name"},
                    {"name": "coordinates", "type": "TEXT", "description": "JSON array of line coordinates"},
                    {"name": "properties", "type": "JSONB", "description": "Additional properties from KML"},
                    {"name": "source_file", "type": "VARCHAR(255)", "description": "Source KML file"},
                    {"name": "created_at", "type": "TIMESTAMP DEFAULT NOW()", "description": "Record creation time"}
                ],
                "indexes": [
                    "CREATE INDEX idx_geographic_lines_name ON geographic_lines(name);"
                ]
            }
        },
        "views": {
            "area_search_view": {
                "description": "View for searching areas by name and location",
                "sql": """
                CREATE VIEW area_search_view AS
                SELECT 
                    id,
                    name,
                    name_arabic,
                    name_english,
                    sector_number,
                    community_number,
                    center_latitude,
                    center_longitude,
                    area_sqm,
                    perimeter_m,
                    source_file
                FROM geographic_areas
                WHERE name IS NOT NULL AND name != '';
                """
            },
            "point_search_view": {
                "description": "View for searching points by name and location",
                "sql": """
                CREATE VIEW point_search_view AS
                SELECT 
                    id,
                    name,
                    latitude,
                    longitude,
                    altitude,
                    source_file
                FROM geographic_points
                WHERE name IS NOT NULL AND name != '';
                """
            }
        },
        "functions": {
            "find_areas_by_coordinates": {
                "description": "Find areas that contain given coordinates",
                "sql": """
                CREATE OR REPLACE FUNCTION find_areas_by_coordinates(
                    lat DECIMAL,
                    lon DECIMAL
                ) RETURNS TABLE(
                    id INTEGER,
                    name VARCHAR,
                    distance DECIMAL
                ) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT 
                        ga.id,
                        ga.name,
                        SQRT(
                            POWER(ga.center_latitude - lat, 2) + 
                            POWER(ga.center_longitude - lon, 2)
                        ) as distance
                    FROM geographic_areas ga
                    ORDER BY distance
                    LIMIT 10;
                END;
                $$ LANGUAGE plpgsql;
                """
            },
            "find_points_within_radius": {
                "description": "Find points within a specified radius of given coordinates",
                "sql": """
                CREATE OR REPLACE FUNCTION find_points_within_radius(
                    center_lat DECIMAL,
                    center_lon DECIMAL,
                    radius_meters DECIMAL
                ) RETURNS TABLE(
                    id INTEGER,
                    name VARCHAR,
                    latitude DECIMAL,
                    longitude DECIMAL,
                    distance_meters DECIMAL
                ) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT 
                        gp.id,
                        gp.name,
                        gp.latitude,
                        gp.longitude,
                        (6371000 * acos(
                            cos(radians(center_lat)) * 
                            cos(radians(gp.latitude)) * 
                            cos(radians(gp.longitude) - radians(center_lon)) + 
                            sin(radians(center_lat)) * 
                            sin(radians(gp.latitude))
                        )) as distance_meters
                    FROM geographic_points gp
                    WHERE (6371000 * acos(
                        cos(radians(center_lat)) * 
                        cos(radians(gp.latitude)) * 
                        cos(radians(gp.longitude) - radians(center_lon)) + 
                        sin(radians(center_lat)) * 
                        sin(radians(gp.latitude))
                    )) <= radius_meters
                    ORDER BY distance_meters;
                END;
                $$ LANGUAGE plpgsql;
                """
            }
        }
    }
    
    # Write schema suggestions to file
    schema_file = output_dir / 'database_schema_suggestions.sql'
    
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write("-- Database Schema Suggestions for KML Data\n")
        f.write("-- Generated from processed KML files\n\n")
        
        # Tables
        f.write("-- TABLES\n")
        f.write("="*50 + "\n\n")
        
        for table_name, table_info in schema_suggestions["tables"].items():
            f.write(f"-- {table_info['description']}\n")
            f.write(f"CREATE TABLE {table_name} (\n")
            
            columns = []
            for col in table_info["columns"]:
                columns.append(f"    {col['name']} {col['type']} -- {col['description']}")
            
            f.write(",\n".join(columns))
            f.write("\n);\n\n")
            
            # Indexes
            if table_info.get("indexes"):
                f.write("-- Indexes for {table_name}\n")
                for index in table_info["indexes"]:
                    f.write(f"{index}\n")
                f.write("\n")
        
        # Views
        f.write("-- VIEWS\n")
        f.write("="*50 + "\n\n")
        
        for view_name, view_info in schema_suggestions["views"].items():
            f.write(f"-- {view_info['description']}\n")
            f.write(f"{view_info['sql']}\n\n")
        
        # Functions
        f.write("-- FUNCTIONS\n")
        f.write("="*50 + "\n\n")
        
        for func_name, func_info in schema_suggestions["functions"].items():
            f.write(f"-- {func_info['description']}\n")
            f.write(f"{func_info['sql']}\n\n")
    
    logger.info(f"Database schema suggestions written to: {schema_file}")

if __name__ == "__main__":
    main() 