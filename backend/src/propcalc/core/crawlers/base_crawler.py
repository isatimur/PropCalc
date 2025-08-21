"""
Base Crawler Class for Property Websites
Implements ethical and legal web scraping practices
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """Configuration for web crawlers"""
    base_url: str
    user_agents: List[str]
    request_delay: float = 2.0  # Seconds between requests
    max_retries: int = 3
    timeout: int = 30
    respect_robots_txt: bool = True
    max_pages_per_session: int = 100
    session_duration: int = 3600  # 1 hour

@dataclass
class PropertyData:
    """Standardized property data structure"""
    source: str
    source_id: str
    url: str
    title: str
    price: Optional[float]
    price_currency: str = "AED"
    location: str
    property_type: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    area_sqft: Optional[float]
    area_sqm: Optional[float]
    developer: Optional[str]
    completion_date: Optional[str]
    description: Optional[str]
    amenities: List[str]
    images: List[str]
    coordinates: Optional[Dict[str, float]]
    listing_date: Optional[str]
    last_updated: Optional[str]
    agent_name: Optional[str]
    agent_phone: Optional[str]
    agent_email: Optional[str]
    verification_status: str = "unverified"
    data_quality_score: Optional[float]
    raw_data: Dict[str, Any]

class BaseCrawler(ABC):
    """Base class for all property website crawlers"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_page = 0
        self.session_start_time = time.time()
        self.request_count = 0
        
        # Ethical scraping settings
        self.user_agents = config.user_agents
        self.request_delay = config.request_delay
        self.max_retries = config.max_retries
        self.timeout = config.timeout
        
        # Robots.txt compliance
        self.robots_txt_cache = {}
        self.allowed_paths = set()
        
        logger.info(f"Initialized crawler for {config.base_url}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def start_session(self):
        """Start aiohttp session with proper headers"""
        if self.session is None:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
            )
            
            # Load robots.txt if enabled
            if self.config.respect_robots_txt:
                await self.load_robots_txt()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def load_robots_txt(self):
        """Load and parse robots.txt file"""
        try:
            robots_url = urljoin(self.config.base_url, '/robots.txt')
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    self._parse_robots_txt(robots_content)
                    logger.info("Loaded robots.txt successfully")
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}")
    
    def _parse_robots_txt(self, content: str):
        """Parse robots.txt content"""
        current_user_agent = None
        for line in content.split('\n'):
            line = line.strip().lower()
            if line.startswith('user-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.startswith('disallow:') and current_user_agent in ['*', '']:
                path = line.split(':', 1)[1].strip()
                self.allowed_paths.add(path)
    
    def is_path_allowed(self, path: str) -> bool:
        """Check if a path is allowed according to robots.txt"""
        if not self.config.respect_robots_txt:
            return True
        
        for disallowed_path in self.allowed_paths:
            if path.startswith(disallowed_path):
                return False
        return True
    
    async def make_request(self, url: str, retry_count: int = 0) -> Optional[aiohttp.ClientResponse]:
        """Make HTTP request with ethical delays and retry logic"""
        if not self.is_path_allowed(urlparse(url).path):
            logger.warning(f"Path not allowed by robots.txt: {url}")
            return None
        
        # Check session limits
        if self._should_reset_session():
            await self._reset_session()
        
        # Ethical delay
        if self.request_count > 0:
            delay = self.request_delay + random.uniform(0, 1)
            await asyncio.sleep(delay)
        
        try:
            # Rotate user agent
            headers = {'User-Agent': random.choice(self.user_agents)}
            
            async with self.session.get(url, headers=headers) as response:
                self.request_count += 1
                
                if response.status == 200:
                    return response
                elif response.status == 429:  # Too Many Requests
                    if retry_count < self.max_retries:
                        wait_time = (2 ** retry_count) * 60  # Exponential backoff
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                        return await self.make_request(url, retry_count + 1)
                    else:
                        logger.error(f"Max retries exceeded for {url}")
                        return None
                else:
                    logger.warning(f"Request failed with status {response.status}: {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self.make_request(url, retry_count + 1)
            return None
    
    def _should_reset_session(self) -> bool:
        """Check if session should be reset"""
        return (
            self.current_page >= self.config.max_pages_per_session or
            time.time() - self.session_start_time >= self.config.session_duration
        )
    
    async def _reset_session(self):
        """Reset session to avoid detection"""
        logger.info("Resetting crawler session")
        await self.close_session()
        await self.start_session()
        self.current_page = 0
        self.session_start_time = time.time()
        self.request_count = 0
    
    @abstractmethod
    async def crawl_properties(self, max_pages: int = 10) -> List[PropertyData]:
        """Crawl properties from the website"""
        pass
    
    @abstractmethod
    async def parse_property_page(self, url: str) -> Optional[PropertyData]:
        """Parse individual property page"""
        pass
    
    @abstractmethod
    async def get_property_links(self, page_url: str) -> List[str]:
        """Extract property links from listing page"""
        pass
    
    def standardize_property_data(self, raw_data: Dict[str, Any]) -> PropertyData:
        """Standardize raw property data"""
        # This method should be implemented by subclasses
        # to convert website-specific data to standard format
        raise NotImplementedError
    
    def calculate_data_quality_score(self, data: PropertyData) -> float:
        """Calculate data quality score (0-100)"""
        score = 0
        required_fields = ['title', 'price', 'location', 'property_type']
        
        # Check required fields
        for field in required_fields:
            if getattr(data, field):
                score += 20
        
        # Check optional fields
        optional_fields = ['bedrooms', 'bathrooms', 'area_sqft', 'developer', 'description']
        for field in optional_fields:
            if getattr(data, field):
                score += 10
        
        # Check data completeness
        if data.amenities:
            score += 5
        if data.images:
            score += 5
        if data.coordinates:
            score += 5
        
        return min(score, 100)
    
    async def save_to_dataframe(self, properties: List[PropertyData]) -> pd.DataFrame:
        """Convert properties to pandas DataFrame"""
        data = []
        for prop in properties:
            row = {
                'source': prop.source,
                'source_id': prop.source_id,
                'url': prop.url,
                'title': prop.title,
                'price': prop.price,
                'price_currency': prop.price_currency,
                'location': prop.location,
                'property_type': prop.property_type,
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'area_sqft': prop.area_sqft,
                'area_sqm': prop.area_sqm,
                'developer': prop.developer,
                'completion_date': prop.completion_date,
                'description': prop.description,
                'amenities': ';'.join(prop.amenities) if prop.amenities else None,
                'images': ';'.join(prop.images) if prop.images else None,
                'latitude': prop.coordinates.get('lat') if prop.coordinates else None,
                'longitude': prop.coordinates.get('lng') if prop.coordinates else None,
                'listing_date': prop.listing_date,
                'last_updated': prop.last_updated,
                'agent_name': prop.agent_name,
                'agent_phone': prop.agent_phone,
                'agent_email': prop.agent_email,
                'verification_status': prop.verification_status,
                'data_quality_score': prop.data_quality_score,
                'crawled_at': pd.Timestamp.now()
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def log_crawling_stats(self, properties: List[PropertyData]):
        """Log crawling statistics"""
        if properties:
            avg_quality = sum(p.data_quality_score or 0 for p in properties) / len(properties)
            logger.info(f"Crawled {len(properties)} properties")
            logger.info(f"Average data quality score: {avg_quality:.2f}")
            logger.info(f"Data sources: {list(set(p.source for p in properties))}")
        else:
            logger.warning("No properties were crawled")
