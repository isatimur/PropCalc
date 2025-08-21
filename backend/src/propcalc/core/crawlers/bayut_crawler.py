"""
Bayut.com Crawler
Implements ethical web scraping for Bayut.com
"""

import re
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd

from .base_crawler import BaseCrawler, CrawlerConfig, PropertyData

logger = logging.getLogger(__name__)

class BayutCrawler(BaseCrawler):
    """Crawler for Bayut.com"""
    
    def __init__(self):
        config = CrawlerConfig(
            base_url="https://www.bayut.com",
            user_agents=[
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ],
            request_delay=2.5,  # Bayut is moderately sensitive
            max_retries=3,
            timeout=30,
            respect_robots_txt=True,
            max_pages_per_session=75,
            session_duration=2400  # 40 minutes
        )
        super().__init__(config)
        
        # Bayut specific selectors
        self.selectors = {
            'property_links': 'a[href*="/property-details-"], .property-link',
            'title': 'h1[data-testid="property-title"], .property-title h1, h1.title',
            'price': '.price, .property-price, [data-testid="price"]',
            'location': '.location, .property-location, [data-testid="location"]',
            'property_type': '.property-type, .type, [data-testid="property-type"]',
            'bedrooms': '.bedrooms, .beds, [data-testid="bedrooms"]',
            'bathrooms': '.bathrooms, .baths, [data-testid="bathrooms"]',
            'area': '.area, .sqft, .sqm, [data-testid="area"]',
            'developer': '.developer, .developer-name, [data-testid="developer"]',
            'description': '.description, .property-description, [data-testid="description"]',
            'amenities': '.amenities li, .features li, [data-testid="amenities"] li',
            'images': '.property-images img, .gallery img, [data-testid="images"] img',
            'agent_name': '.agent-name, .broker-name, [data-testid="agent-name"]',
            'agent_phone': '.agent-phone, .broker-phone, [data-testid="agent-phone"]',
            'agent_email': '.agent-email, .broker-email, [data-testid="agent-email"]',
            'listing_date': '.listing-date, .date-added, [data-testid="listing-date"]',
            'coordinates': '.map-coordinates, [data-lat], [data-lng], [data-testid="coordinates"]',
            'completion_date': '.completion-date, .handover, [data-testid="completion-date"]'
        }
    
    async def crawl_properties(self, max_pages: int = 10) -> List[PropertyData]:
        """Crawl properties from Bayut.com"""
        properties = []
        
        try:
            # Start with main property listing page
            base_listing_url = f"{self.config.base_url}/for-sale/properties/dubai/"
            
            for page in range(1, max_pages + 1):
                logger.info(f"Crawling Bayut page {page}")
                
                # Construct page URL
                if page == 1:
                    page_url = base_listing_url
                else:
                    page_url = f"{base_listing_url}page-{page}/"
                
                # Get property links from listing page
                property_links = await self.get_property_links(page_url)
                
                if not property_links:
                    logger.warning(f"No property links found on page {page}")
                    break
                
                # Parse each property page
                for link in property_links[:6]:  # Limit to 6 properties per page for ethical scraping
                    try:
                        property_data = await self.parse_property_page(link)
                        if property_data:
                            properties.append(property_data)
                            logger.info(f"Parsed property: {property_data.title}")
                    except Exception as e:
                        logger.error(f"Error parsing property {link}: {e}")
                        continue
                
                self.current_page = page
                
                # Check if we should continue
                if len(property_links) < 15:  # Less than 15 properties means we're at the end
                    break
                    
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
        
        # Calculate data quality scores
        for prop in properties:
            prop.data_quality_score = self.calculate_data_quality_score(prop)
        
        self.log_crawling_stats(properties)
        return properties
    
    async def get_property_links(self, page_url: str) -> List[str]:
        """Extract property links from listing page"""
        try:
            response = await self.make_request(page_url)
            if not response:
                return []
            
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find property links
            property_links = []
            link_elements = soup.select(self.selectors['property_links'])
            
            for link in link_elements:
                href = link.get('href')
                if href and '/property-details-' in href:
                    full_url = urljoin(self.config.base_url, href)
                    if full_url not in property_links:
                        property_links.append(full_url)
            
            logger.info(f"Found {len(property_links)} property links on {page_url}")
            return property_links
            
        except Exception as e:
            logger.error(f"Error extracting property links from {page_url}: {e}")
            return []
    
    async def parse_property_page(self, url: str) -> Optional[PropertyData]:
        """Parse individual property page"""
        try:
            response = await self.make_request(url)
            if not response:
                return None
            
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract property data
            raw_data = self._extract_raw_data(soup, url)
            
            # Standardize the data
            property_data = self.standardize_property_data(raw_data)
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error parsing property page {url}: {e}")
            return None
    
    def _extract_raw_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract raw data from BeautifulSoup object"""
        raw_data = {'url': url}
        
        # Extract title
        title_elem = soup.select_one(self.selectors['title'])
        raw_data['title'] = title_elem.get_text(strip=True) if title_elem else None
        
        # Extract price
        price_elem = soup.select_one(self.selectors['price'])
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            raw_data['price'] = self._extract_price(price_text)
        
        # Extract location
        location_elem = soup.select_one(self.selectors['location'])
        raw_data['location'] = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract property type
        type_elem = soup.select_one(self.selectors['property_type'])
        raw_data['property_type'] = type_elem.get_text(strip=True) if type_elem else None
        
        # Extract bedrooms
        beds_elem = soup.select_one(self.selectors['bedrooms'])
        if beds_elem:
            raw_data['bedrooms'] = self._extract_number(beds_elem.get_text())
        
        # Extract bathrooms
        baths_elem = soup.select_one(self.selectors['bathrooms'])
        if baths_elem:
            raw_data['bathrooms'] = self._extract_number(baths_elem.get_text())
        
        # Extract area
        area_elem = soup.select_one(self.selectors['area'])
        if area_elem:
            area_text = area_elem.get_text(strip=True)
            raw_data['area_sqft'], raw_data['area_sqm'] = self._extract_area(area_text)
        
        # Extract developer
        dev_elem = soup.select_one(self.selectors['developer'])
        raw_data['developer'] = dev_elem.get_text(strip=True) if dev_elem else None
        
        # Extract completion date (Bayut often provides this)
        completion_elem = soup.select_one(self.selectors['completion_date'])
        raw_data['completion_date'] = completion_elem.get_text(strip=True) if completion_elem else None
        
        # Extract description
        desc_elem = soup.select_one(self.selectors['description'])
        raw_data['description'] = desc_elem.get_text(strip=True) if desc_elem else None
        
        # Extract amenities
        amenities_elems = soup.select(self.selectors['amenities'])
        raw_data['amenities'] = [elem.get_text(strip=True) for elem in amenities_elems if elem.get_text(strip=True)]
        
        # Extract images
        image_elems = soup.select(self.selectors['images'])
        raw_data['images'] = []
        for img in image_elems:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                full_src = urljoin(self.config.base_url, src)
                raw_data['images'].append(full_src)
        
        # Extract agent information
        agent_name_elem = soup.select_one(self.selectors['agent_name'])
        raw_data['agent_name'] = agent_name_elem.get_text(strip=True) if agent_name_elem else None
        
        agent_phone_elem = soup.select_one(self.selectors['agent_phone'])
        raw_data['agent_phone'] = agent_phone_elem.get_text(strip=True) if agent_phone_elem else None
        
        agent_email_elem = soup.select_one(self.selectors['agent_email'])
        raw_data['agent_email'] = agent_email_elem.get_text(strip=True) if agent_email_elem else None
        
        # Extract listing date
        date_elem = soup.select_one(self.selectors['listing_date'])
        raw_data['listing_date'] = date_elem.get_text(strip=True) if date_elem else None
        
        # Extract coordinates
        coords_elem = soup.select_one(self.selectors['coordinates'])
        if coords_elem:
            raw_data['coordinates'] = self._extract_coordinates(coords_elem)
        
        # Generate source ID from URL
        raw_data['source_id'] = self._generate_source_id(url)
        
        return raw_data
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols, commas, and common text
        price_text = re.sub(r'[^\d,.]', '', price_text)
        price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group().replace(',', ''))
            except ValueError:
                pass
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract numeric value from text"""
        if not text:
            return None
        
        number_match = re.search(r'\d+', text)
        if number_match:
            try:
                return int(number_match.group())
            except ValueError:
                pass
        return None
    
    def _extract_area(self, area_text: str) -> tuple[Optional[float], Optional[float]]:
        """Extract area in sqft and sqm"""
        if not area_text:
            return None, None
        
        # Look for sqft
        sqft_match = re.search(r'(\d+(?:,\d+)*)\s*sq\s*ft', area_text, re.IGNORECASE)
        sqft = None
        if sqft_match:
            try:
                sqft = float(sqft_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # Look for sqm
        sqm_match = re.search(r'(\d+(?:,\d+)*)\s*sq\s*m', area_text, re.IGNORECASE)
        sqm = None
        if sqm_match:
            try:
                sqm = float(sqm_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # If no specific unit found, try to extract any number
        if sqft is None and sqm is None:
            area_match = re.search(r'(\d+(?:,\d+)*)', area_text)
            if area_match:
                try:
                    area_value = float(area_match.group(1).replace(',', ''))
                    # Assume sqft if no unit specified (common in UAE)
                    sqft = area_value
                except ValueError:
                    pass
        
        return sqft, sqm
    
    def _extract_coordinates(self, elem) -> Optional[Dict[str, float]]:
        """Extract coordinates from element"""
        try:
            # Try data attributes first
            lat = elem.get('data-lat')
            lng = elem.get('data-lng')
            
            if lat and lng:
                return {'lat': float(lat), 'lng': float(lng)}
            
            # Try text content
            coords_text = elem.get_text(strip=True)
            coords_match = re.search(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', coords_text)
            if coords_match:
                return {'lat': float(coords_match.group(1)), 'lng': float(coords_match.group(2))}
                
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def _generate_source_id(self, url: str) -> str:
        """Generate unique source ID from URL"""
        # Extract property ID from URL
        property_match = re.search(r'/property-details-([^/?]+)', url)
        if property_match:
            return f"bayut_{property_match.group(1)}"
        
        # Fallback to URL hash
        return f"bayut_{hash(url) % 1000000}"
    
    def standardize_property_data(self, raw_data: Dict[str, Any]) -> PropertyData:
        """Standardize Bayut data to common format"""
        return PropertyData(
            source="bayut.com",
            source_id=raw_data.get('source_id', ''),
            url=raw_data.get('url', ''),
            title=raw_data.get('title', ''),
            price=raw_data.get('price'),
            price_currency="AED",
            location=raw_data.get('location', ''),
            property_type=raw_data.get('property_type', ''),
            bedrooms=raw_data.get('bedrooms'),
            bathrooms=raw_data.get('bathrooms'),
            area_sqft=raw_data.get('area_sqft'),
            area_sqm=raw_data.get('area_sqm'),
            developer=raw_data.get('developer'),
            completion_date=raw_data.get('completion_date'),
            description=raw_data.get('description'),
            amenities=raw_data.get('amenities', []),
            images=raw_data.get('images', []),
            coordinates=raw_data.get('coordinates'),
            listing_date=raw_data.get('listing_date'),
            last_updated=None,  # Will be set to current time
            agent_name=raw_data.get('agent_name'),
            agent_phone=raw_data.get('agent_phone'),
            agent_email=raw_data.get('agent_email'),
            verification_status="unverified",
            data_quality_score=None,  # Will be calculated later
            raw_data=raw_data
        )
