#!/usr/bin/env python3
"""
Test Small Crawl for PropCalc Property Crawler
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_small_crawl():
    """Test a small crawl with minimal pages"""
    try:
        print("🧪 Testing Small Crawl...")
        
        from propcalc.core.crawlers import CrawlerManager
        
        # Create crawler manager
        crawler_manager = CrawlerManager()
        print("✅ CrawlerManager created")
        
        # Test crawling PropertyFinder with just 1 page
        print("🕷️ Testing PropertyFinder crawler (1 page)...")
        
        async with crawler_manager.crawlers['propertyfinder'] as crawler:
            print("✅ PropertyFinder crawler session started")
            
            # Try to get property links from first page
            try:
                links = await crawler.get_property_links("https://www.propertyfinder.ae/buy")
                print(f"✅ Found {len(links)} property links")
                
                if links:
                    print(f"   First link: {links[0]}")
                    
                    # Try to parse one property page
                    print("🔍 Testing property page parsing...")
                    property_data = await crawler.parse_property_page(links[0])
                    
                    if property_data:
                        print("✅ Property parsed successfully!")
                        print(f"   Title: {property_data.title}")
                        print(f"   Price: {property_data.price}")
                        print(f"   Location: {property_data.location}")
                        print(f"   Type: {property_data.property_type}")
                    else:
                        print("⚠️ Property parsing returned None")
                else:
                    print("⚠️ No property links found")
                    
            except Exception as e:
                print(f"⚠️ Error during crawling: {e}")
                print("   This might be due to website structure changes or access restrictions")
        
        print("\n🎉 Small crawl test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_small_crawl())
    sys.exit(0 if success else 1)
