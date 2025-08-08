#!/usr/bin/env python3
"""
Script to setup DLD-KML integration
Connects DLD area data with KML geographic data for location-based real estate analysis
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from propcalc.core.dld_kml_integration import DLDKMLIntegration
import psycopg2

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dld_kml_integration.log'),
            logging.StreamHandler()
        ]
    )

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        user=os.getenv('POSTGRES_USER', 'vantage_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'vantage_password'),
        database=os.getenv('POSTGRES_DB', 'vantage_ai')
    )

def main():
    """Main function to setup DLD-KML integration"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize database connection
        db_connection = get_db_connection()
        dld_kml = DLDKMLIntegration(db_connection)
        
        logger.info("Starting DLD-KML integration setup...")
        
        # Create integration tables
        logger.info("Creating integration tables...")
        dld_kml.create_integration_tables()
        
        # Get data counts
        dld_areas = dld_kml.get_dld_areas()
        geographic_areas = dld_kml.get_geographic_areas()
        
        logger.info(f"Found {len(dld_areas)} DLD areas")
        logger.info(f"Found {len(geographic_areas)} geographic areas")
        
        # Find area matches
        logger.info("Finding area matches...")
        matches = dld_kml.find_area_matches()
        
        # Save matches
        logger.info(f"Saving {len(matches)} area matches...")
        dld_kml.save_area_matches(matches)
        
        # Update market statistics
        logger.info("Updating market statistics...")
        dld_kml.update_area_market_statistics()
        
        # Print summary
        print("\n" + "="*50)
        print("DLD-KML INTEGRATION SETUP SUMMARY")
        print("="*50)
        print(f"DLD Areas: {len(dld_areas)}")
        print(f"Geographic Areas: {len(geographic_areas)}")
        print(f"Area Matches Found: {len(matches)}")
        
        # Show some example matches
        print(f"\nExample Matches:")
        for i, match in enumerate(matches[:10]):
            print(f"  {i+1}. {match.dld_area.name_en} ↔ {match.geographic_area.name_english}")
            print(f"     Confidence: {match.confidence_score:.2f} ({match.match_type})")
        
        # Show match statistics
        match_types = {}
        for match in matches:
            match_types[match.match_type] = match_types.get(match.match_type, 0) + 1
        
        print(f"\nMatch Types:")
        for match_type, count in match_types.items():
            print(f"  {match_type}: {count} matches")
        
        # Test some functionality
        print(f"\nTesting Integration:")
        
        # Test area market data
        if matches:
            test_area_id = matches[0].dld_area.area_id
            market_data = dld_kml.get_area_market_statistics(test_area_id)
            print(f"  Market data for area {test_area_id}: {len(market_data.get('property_types', []))} property types")
        
        # Test location search
        test_areas = dld_kml.search_areas_by_location(25.2048, 55.2708, 5.0)  # Dubai coordinates
        print(f"  Areas near Dubai center: {len(test_areas)} found")
        
        db_connection.close()
        
        print(f"\n✅ DLD-KML integration setup completed successfully!")
        print(f"   - API endpoints available at /api/dld-kml/")
        print(f"   - Location-based searches enabled")
        print(f"   - Market statistics updated")
        
    except Exception as e:
        logger.error(f"Error setting up DLD-KML integration: {e}")
        raise

if __name__ == "__main__":
    main() 