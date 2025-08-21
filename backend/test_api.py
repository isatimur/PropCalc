#!/usr/bin/env python3
"""
Test API Endpoints for PropCalc Property Crawler
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_api():
    """Test API endpoints"""
    try:
        print("🧪 Testing PropCalc Crawler API...")
        
        from propcalc.api.crawler_api import router
        print("✅ API router imported successfully")
        
        # Test that we can create a crawler manager
        from propcalc.core.crawlers import CrawlerManager
        crawler_manager = CrawlerManager()
        print("✅ CrawlerManager created")
        
        # Test API endpoints
        print("\n📡 Testing API endpoints:")
        
        # Test health endpoint
        from propcalc.api.crawler_api import crawler_health
        health_response = await crawler_health()
        print(f"✅ Health endpoint: {health_response}")
        
        # Test sources endpoint
        from propcalc.api.crawler_api import get_crawler_sources
        sources_response = await get_crawler_sources(crawler_manager)
        print(f"✅ Sources endpoint: {len(sources_response.get('available_sources', []))} sources")
        
        # Test data quality endpoint
        from propcalc.api.crawler_api import get_data_quality_metrics
        quality_response = await get_data_quality_metrics(source=None, crawler_manager=crawler_manager)
        print(f"✅ Data quality endpoint: {quality_response.get('total_sources', 0)} sources")
        
        print("\n🎉 All API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    sys.exit(0 if success else 1)
