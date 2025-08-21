#!/usr/bin/env python3
"""
Demo Script for PropCalc Property Crawler System
Tests the crawler functionality with minimal data collection
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from propcalc.core.crawlers import CrawlerManager
from propcalc.core.crawlers.base_crawler import PropertyData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_single_source_crawl():
    """Demo crawling a single source with minimal pages"""
    logger.info("🚀 Starting single source crawl demo...")
    
    try:
        crawler_manager = CrawlerManager()
        
        # Crawl PropertyFinder with just 2 pages
        logger.info("📊 Crawling PropertyFinder.ae (2 pages)...")
        properties = await crawler_manager.crawl_single_source("propertyfinder", max_pages=2)
        
        if properties:
            logger.info(f"✅ Found {len(properties)} properties from PropertyFinder")
            
            # Show sample data
            for i, prop in enumerate(properties[:3]):  # Show first 3
                logger.info(f"🏠 Property {i+1}:")
                logger.info(f"   Title: {prop.title}")
                logger.info(f"   Price: {prop.price} {prop.price_currency}")
                logger.info(f"   Location: {prop.location}")
                logger.info(f"   Type: {prop.property_type}")
                logger.info(f"   Beds: {prop.bedrooms}, Baths: {prop.bathrooms}")
                logger.info(f"   Area: {prop.area_sqft} sqft / {prop.area_sqm} sqm")
                logger.info(f"   Quality Score: {prop.data_quality_score}")
                logger.info("")
        else:
            logger.warning("⚠️ No properties found from PropertyFinder")
        
        # Crawl Bayut with just 2 pages
        logger.info("📊 Crawling Bayut.com (2 pages)...")
        properties = await crawler_manager.crawl_single_source("bayut", max_pages=2)
        
        if properties:
            logger.info(f"✅ Found {len(properties)} properties from Bayut")
            
            # Show sample data
            for i, prop in enumerate(properties[:3]):  # Show first 3
                logger.info(f"🏠 Property {i+1}:")
                logger.info(f"   Title: {prop.title}")
                logger.info(f"   Price: {prop.price} {prop.price_currency}")
                logger.info(f"   Location: {prop.location}")
                logger.info(f"   Type: {prop.property_type}")
                logger.info(f"   Beds: {prop.bedrooms}, Baths: {prop.bathrooms}")
                logger.info(f"   Area: {prop.area_sqft} sqft / {prop.area_sqm} sqm")
                logger.info(f"   Quality Score: {prop.data_quality_score}")
                logger.info("")
        else:
            logger.warning("⚠️ No properties found from Bayut")
        
    except Exception as e:
        logger.error(f"❌ Error during single source crawl: {e}")
        raise

async def demo_data_aggregation():
    """Demo data aggregation and analysis"""
    logger.info("🔄 Starting data aggregation demo...")
    
    try:
        crawler_manager = CrawlerManager()
        
        # Get data summary
        summary = crawler_manager.get_data_summary()
        logger.info("📊 Data Summary:")
        logger.info(f"   Total Sources: {summary['total_sources']}")
        logger.info(f"   Crawled Sources: {summary['crawled_sources']}")
        logger.info(f"   Total Properties: {summary['total_properties']}")
        
        if summary['source_breakdown']:
            logger.info("   Source Breakdown:")
            for source, count in summary['source_breakdown'].items():
                logger.info(f"     {source}: {count} properties")
        
        if summary['data_quality']:
            logger.info("   Data Quality:")
            for metric, value in summary['data_quality'].items():
                logger.info(f"     {metric}: {value}")
        
        if summary['price_ranges']:
            logger.info("   Price Ranges:")
            for metric, value in summary['price_ranges'].items():
                logger.info(f"     {metric}: {value:,.0f} AED")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Error during data aggregation: {e}")
        raise

async def demo_similarity_search():
    """Demo finding similar properties"""
    logger.info("🔍 Starting similarity search demo...")
    
    try:
        crawler_manager = CrawlerManager()
        
        # Create a sample target property
        target_property = PropertyData(
            source="demo",
            source_id="demo_001",
            url="https://demo.com/property/001",
            title="Sample 2BR Apartment in Dubai Marina",
            price=1500000.0,
            price_currency="AED",
            location="Dubai Marina",
            property_type="Apartment",
            bedrooms=2,
            bathrooms=2,
            area_sqft=1200.0,
            area_sqm=111.5,
            developer="Emaar",
            completion_date="2024",
            description="Luxury apartment in Dubai Marina",
            amenities=["Pool", "Gym", "Parking"],
            images=[],
            coordinates={"lat": 25.0920, "lng": 55.1381},
            listing_date="2024-01-01",
            last_updated=None,
            agent_name="Demo Agent",
            agent_phone="+971501234567",
            agent_email="demo@example.com",
            verification_status="verified",
            data_quality_score=95.0,
            raw_data={}
        )
        
        logger.info(f"🎯 Target Property: {target_property.title}")
        logger.info(f"   Location: {target_property.location}")
        logger.info(f"   Type: {target_property.property_type}")
        logger.info(f"   Beds: {target_property.bedrooms}, Baths: {target_property.bathrooms}")
        logger.info(f"   Area: {target_property.area_sqft} sqft")
        logger.info(f"   Price: {target_property.price:,.0f} AED")
        logger.info("")
        
        # Find similar properties
        similar_properties = crawler_manager.find_similar_properties(
            target_property, 
            similarity_threshold=0.6
        )
        
        if similar_properties:
            logger.info(f"🔍 Found {len(similar_properties)} similar properties:")
            for i, prop in enumerate(similar_properties[:5]):  # Show top 5
                similarity = prop.data_quality_score or 0
                logger.info(f"   {i+1}. {prop.title}")
                logger.info(f"      Similarity: {similarity:.1%}")
                logger.info(f"      Price: {prop.price:,.0f} AED" if prop.price else "      Price: N/A")
                logger.info(f"      Location: {prop.location}")
                logger.info("")
        else:
            logger.info("🔍 No similar properties found")
        
    except Exception as e:
        logger.error(f"❌ Error during similarity search: {e}")
        raise

async def demo_crawler_status():
    """Demo crawler status and configuration"""
    logger.info("📊 Starting crawler status demo...")
    
    try:
        crawler_manager = CrawlerManager()
        
        # Get crawler status
        status = crawler_manager.get_crawler_status()
        logger.info("🤖 Crawler Status:")
        
        for source_name, source_status in status.items():
            logger.info(f"   {source_name.upper()}:")
            logger.info(f"     Base URL: {source_status['base_url']}")
            logger.info(f"     Request Delay: {source_status['request_delay']}s")
            logger.info(f"     Max Retries: {source_status['max_retries']}")
            logger.info(f"     Respects Robots.txt: {source_status['respect_robots_txt']}")
            logger.info(f"     Current Page: {source_status['current_page']}")
            logger.info(f"     Request Count: {source_status['request_count']}")
            logger.info(f"     Session Active: {source_status['session_active']}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Error getting crawler status: {e}")
        raise

async def main():
    """Main demo function"""
    logger.info("🎉 PropCalc Property Crawler Demo v2.1.0")
    logger.info("=" * 50)
    logger.info("This demo will test the crawler system with minimal data collection")
    logger.info("⚠️  Please ensure you have proper permissions and respect website terms")
    logger.info("")
    
    try:
        # Run demos
        await demo_crawler_status()
        await demo_single_source_crawl()
        await demo_data_aggregation()
        await demo_similarity_search()
        
        logger.info("✅ All demos completed successfully!")
        logger.info("📁 Check the 'data/crawled' directory for output files")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
