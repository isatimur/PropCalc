"""
Production Configuration for PropCalc Property Crawlers
Optimized for real-world deployment with anti-bot detection handling
"""

import os
from typing import List, Dict, Any
from pydantic import BaseSettings, Field

class CrawlerSettings(BaseSettings):
    """Production crawler configuration settings"""
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://vantage_user:vantage_password@localhost:5433/vantage_ai",
        description="PostgreSQL connection string"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6380/0",
        description="Redis connection string"
    )
    
    # Crawler Performance Settings
    MAX_CONCURRENT_CRAWLERS: int = Field(
        default=3,
        description="Maximum number of concurrent crawler instances"
    )
    
    REQUEST_DELAY_MIN: float = Field(
        default=3.0,
        description="Minimum delay between requests (seconds)"
    )
    
    REQUEST_DELAY_MAX: float = Field(
        default=7.0,
        description="Maximum delay between requests (seconds)"
    )
    
    MAX_RETRIES: int = Field(
        default=5,
        description="Maximum retry attempts for failed requests"
    )
    
    SESSION_TIMEOUT: int = Field(
        default=1800,
        description="Session timeout in seconds (30 minutes)"
    )
    
    MAX_PAGES_PER_SESSION: int = Field(
        default=50,
        description="Maximum pages to crawl per session"
    )
    
    # Anti-Bot Detection Settings
    USER_AGENT_ROTATION: bool = Field(
        default=True,
        description="Enable user agent rotation"
    )
    
    PROXY_ROTATION: bool = Field(
        default=False,
        description="Enable proxy rotation (requires proxy list)"
    )
    
    CAPTCHA_HANDLING: bool = Field(
        default=True,
        description="Enable CAPTCHA detection and handling"
    )
    
    # Data Quality Settings
    MIN_DATA_QUALITY_SCORE: float = Field(
        default=70.0,
        description="Minimum data quality score for properties"
    )
    
    DATA_VALIDATION_ENABLED: bool = Field(
        default=True,
        description="Enable data validation and cleaning"
    )
    
    DUPLICATE_DETECTION: bool = Field(
        default=True,
        description="Enable duplicate property detection"
    )
    
    # Monitoring and Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level for crawler operations"
    )
    
    METRICS_ENABLED: bool = Field(
        default=True,
        description="Enable performance metrics collection"
    )
    
    ALERTING_ENABLED: bool = Field(
        default=True,
        description="Enable alerting for crawler failures"
    )
    
    # Legal and Compliance
    RESPECT_ROBOTS_TXT: bool = Field(
        default=True,
        description="Respect robots.txt files"
    )
    
    MAX_REQUESTS_PER_HOUR: int = Field(
        default=1000,
        description="Maximum requests per hour per domain"
    )
    
    CRAWL_DURING_BUSINESS_HOURS: bool = Field(
        default=False,
        description="Limit crawling to business hours (9 AM - 6 PM UAE time)"
    )
    
    # Storage and Output
    OUTPUT_DIRECTORY: str = Field(
        default="data/crawled",
        description="Directory for storing crawled data"
    )
    
    DATA_RETENTION_DAYS: int = Field(
        default=90,
        description="Number of days to retain crawled data"
    )
    
    BACKUP_ENABLED: bool = Field(
        default=True,
        description="Enable automatic data backup"
    )
    
    # API Configuration
    API_RATE_LIMIT: int = Field(
        default=100,
        description="API requests per minute"
    )
    
    API_TIMEOUT: int = Field(
        default=30,
        description="API request timeout in seconds"
    )
    
    # Advanced Features
    SIMILARITY_SEARCH_ENABLED: bool = Field(
        default=True,
        description="Enable property similarity search"
    )
    
    MARKET_ANALYSIS_ENABLED: bool = Field(
        default=True,
        description="Enable market trend analysis"
    )
    
    PRICE_PREDICTION_ENABLED: bool = Field(
        default=False,
        description="Enable price prediction models"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "CRAWLER_"

# Production user agents for rotation
PRODUCTION_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
]

# UAE-specific locations for data validation
UAE_LOCATIONS = [
    "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah",
    "Dubai Marina", "Palm Jumeirah", "Downtown Dubai", "Business Bay", "Jumeirah Beach Residence",
    "Dubai Hills Estate", "Emirates Hills", "Arabian Ranches", "Meadows", "Springs", "Lakes", "Greens"
]

# Property types for categorization
PROPERTY_TYPES = [
    "Apartment", "Villa", "Townhouse", "Penthouse", "Studio", "Duplex", "Compound", "Bungalow"
]

# Amenities for data enrichment
PROPERTY_AMENITIES = [
    "Swimming Pool", "Gym", "Parking", "Security", "Garden", "Balcony", "Central AC",
    "Furnished", "Pet Friendly", "Children's Play Area", "BBQ Area", "Tennis Court",
    "Spa", "Concierge", "Valet Parking", "Elevator", "Storage", "Maid's Room"
]

# Developer reputation scores
DEVELOPER_REPUTATION = {
    "Emaar": 95,
    "Nakheel": 90,
    "Meraas": 88,
    "Damac": 85,
    "Sobha": 87,
    "Azizi": 82,
    "Binghatti": 80,
    "Ellington": 85,
    "Omniyat": 88,
    "Select Group": 83,
    "DAMAC Properties": 85,
}

# Price ranges for UAE properties (AED)
PRICE_RANGES = {
    "budget": {"min": 300000, "max": 800000},
    "mid_range": {"min": 800000, "max": 2000000},
    "high_end": {"min": 2000000, "max": 5000000},
    "luxury": {"min": 5000000, "max": 15000000},
    "ultra_luxury": {"min": 15000000, "max": 100000000}
}

# Data quality scoring weights
QUALITY_SCORING_WEIGHTS = {
    "price": 0.25,
    "location": 0.20,
    "property_type": 0.15,
    "bedrooms": 0.10,
    "bathrooms": 0.10,
    "area": 0.10,
    "images": 0.05,
    "description": 0.05
}

# Crawler health check thresholds
HEALTH_CHECK_THRESHOLDS = {
    "success_rate": 0.80,  # 80% success rate required
    "response_time": 5.0,   # 5 seconds max response time
    "error_rate": 0.20,     # 20% max error rate
    "data_quality": 0.70    # 70% min data quality score
}

# Export configuration
crawler_settings = CrawlerSettings()

def get_crawler_config() -> Dict[str, Any]:
    """Get crawler configuration as dictionary"""
    return crawler_settings.dict()

def validate_crawler_config() -> bool:
    """Validate crawler configuration settings"""
    try:
        # Validate required settings
        if crawler_settings.REQUEST_DELAY_MIN < 1.0:
            raise ValueError("Request delay must be at least 1 second")
        
        if crawler_settings.MAX_RETRIES < 1:
            raise ValueError("Max retries must be at least 1")
        
        if crawler_settings.MAX_PAGES_PER_SESSION < 10:
            raise ValueError("Max pages per session must be at least 10")
        
        return True
    except Exception as e:
        print(f"❌ Crawler configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    # Test configuration
    print("🧪 Testing PropCalc Crawler Configuration...")
    
    if validate_crawler_config():
        print("✅ Configuration validation passed")
        print(f"📊 Max concurrent crawlers: {crawler_settings.MAX_CONCURRENT_CRAWLERS}")
        print(f"⏱️ Request delay: {crawler_settings.REQUEST_DELAY_MIN}-{crawler_settings.REQUEST_DELAY_MAX}s")
        print(f"🔄 Max retries: {crawler_settings.MAX_RETRIES}")
        print(f"📈 Min data quality: {crawler_settings.MIN_DATA_QUALITY_SCORE}%")
    else:
        print("❌ Configuration validation failed")
        exit(1)
