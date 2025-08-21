#!/usr/bin/env python3
"""
Simple Test Script for PropCalc Property Crawler
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_crawler():
    """Test basic crawler functionality"""
    try:
        print("🧪 Testing PropCalc Crawler System...")
        
        # Test imports
        from propcalc.core.crawlers import CrawlerManager
        print("✅ Imports working")
        
        # Test crawler manager creation
        crawler_manager = CrawlerManager()
        print("✅ CrawlerManager created")
        
        # Test getting sources
        sources = list(crawler_manager.crawlers.keys())
        print(f"✅ Available sources: {sources}")
        
        # Test crawler status
        status = crawler_manager.get_crawler_status()
        print(f"✅ Crawler status retrieved for {len(status)} sources")
        
        # Test data summary
        summary = crawler_manager.get_data_summary()
        print(f"✅ Data summary: {summary['total_sources']} sources, {summary['total_properties']} properties")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_crawler())
    sys.exit(0 if success else 1)
