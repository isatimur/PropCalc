"""
Property Data Models for PropCalc
Database models for storing crawled property data
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class Property(Base):
    """Main property table for storing crawled property data"""
    __tablename__ = "properties"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Source identification
    source = Column(String(100), nullable=False, index=True)  # e.g., 'propertyfinder.ae', 'bayut.com'
    source_id = Column(String(200), nullable=False, index=True)  # Unique ID from source
    url = Column(Text, nullable=False, unique=True)
    
    # Basic property information
    title = Column(String(500), nullable=False)
    price = Column(Float, nullable=True, index=True)
    price_currency = Column(String(10), default="AED")
    location = Column(String(300), nullable=False, index=True)
    property_type = Column(String(100), nullable=False, index=True)
    
    # Property specifications
    bedrooms = Column(Integer, nullable=True, index=True)
    bathrooms = Column(Integer, nullable=True, index=True)
    area_sqft = Column(Float, nullable=True, index=True)
    area_sqm = Column(Float, nullable=True, index=True)
    
    # Developer and completion
    developer = Column(String(200), nullable=True, index=True)
    completion_date = Column(String(100), nullable=True)
    
    # Description and details
    description = Column(Text, nullable=True)
    amenities = Column(ARRAY(String), nullable=True)  # PostgreSQL array of amenities
    
    # Images and media
    images = Column(ARRAY(String), nullable=True)  # PostgreSQL array of image URLs
    
    # Geographic coordinates
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    # Listing information
    listing_date = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Agent information
    agent_name = Column(String(200), nullable=True)
    agent_phone = Column(String(50), nullable=True)
    agent_email = Column(String(200), nullable=True)
    
    # Data quality and verification
    verification_status = Column(String(50), default="unverified", index=True)
    data_quality_score = Column(Float, nullable=True, index=True)
    
    # Raw data storage
    raw_data = Column(JSON, nullable=True)  # Store original crawled data
    
    # Timestamps
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    price_history = relationship("PropertyPriceHistory", back_populates="property")
    similar_properties = relationship("PropertySimilarity", 
                                   foreign_keys="PropertySimilarity.property_id",
                                   back_populates="property")
    
    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', source='{self.source}')>"

class PropertyPriceHistory(Base):
    """Track price changes for properties over time"""
    __tablename__ = "property_price_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, nullable=False, index=True)
    price = Column(Float, nullable=False)
    price_currency = Column(String(10), default="AED")
    change_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_type = Column(String(50), nullable=True)  # 'increase', 'decrease', 'new_listing'
    change_amount = Column(Float, nullable=True)  # Absolute change amount
    change_percentage = Column(Float, nullable=True)  # Percentage change
    
    # Relationship
    property = relationship("Property", back_populates="price_history")
    
    def __repr__(self):
        return f"<PropertyPriceHistory(property_id={self.property_id}, price={self.price}, date={self.change_date})>"

class PropertySimilarity(Base):
    """Store similarity relationships between properties"""
    __tablename__ = "property_similarities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, nullable=False, index=True)
    similar_property_id = Column(Integer, nullable=False, index=True)
    similarity_score = Column(Float, nullable=False, index=True)
    similarity_factors = Column(JSON, nullable=True)  # Store which factors contributed to similarity
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    property = relationship("Property", foreign_keys=[property_id], back_populates="similar_properties")
    similar_property = relationship("Property", foreign_keys=[similar_property_id])
    
    def __repr__(self):
        return f"<PropertySimilarity(property_id={self.property_id}, similar_id={self.similar_property_id}, score={self.similarity_score})>"

class CrawlSession(Base):
    """Track crawling sessions and their results"""
    __tablename__ = "crawl_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False, index=True)
    session_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_end = Column(DateTime, nullable=True)
    status = Column(String(50), default="running", index=True)  # 'running', 'completed', 'failed'
    
    # Crawling statistics
    pages_crawled = Column(Integer, default=0)
    properties_found = Column(Integer, default=0)
    properties_parsed = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    
    # Configuration used
    max_pages = Column(Integer, nullable=True)
    request_delay = Column(Float, nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Error details
    error_details = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CrawlSession(id={self.id}, source='{self.source}', status='{self.status}')>"

class DataQualityMetrics(Base):
    """Track data quality metrics for crawled properties"""
    __tablename__ = "data_quality_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False, index=True)
    crawl_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Quality metrics
    total_properties = Column(Integer, default=0)
    properties_with_price = Column(Integer, default=0)
    properties_with_location = Column(Integer, default=0)
    properties_with_coordinates = Column(Integer, default=0)
    properties_with_images = Column(Integer, default=0)
    properties_with_amenities = Column(Integer, default=0)
    
    # Average scores
    avg_data_quality_score = Column(Float, nullable=True)
    avg_price_completeness = Column(Float, nullable=True)
    avg_location_completeness = Column(Float, nullable=True)
    
    # Data freshness
    newest_listing_date = Column(DateTime, nullable=True)
    oldest_listing_date = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DataQualityMetrics(source='{self.source}', date={self.crawl_date})>"

class MarketTrends(Base):
    """Aggregated market trends and statistics"""
    __tablename__ = "market_trends"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(300), nullable=False, index=True)
    property_type = Column(String(100), nullable=False, index=True)
    
    # Price trends
    avg_price = Column(Float, nullable=True)
    median_price = Column(Float, nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    price_per_sqft = Column(Float, nullable=True)
    
    # Market activity
    total_listings = Column(Integer, default=0)
    new_listings = Column(Integer, default=0)
    price_changes = Column(Integer, default=0)
    
    # Time on market (estimated)
    avg_days_on_market = Column(Float, nullable=True)
    
    # Market indicators
    market_activity_score = Column(Float, nullable=True)  # 0-100 scale
    price_volatility = Column(Float, nullable=True)  # Standard deviation of prices
    
    def __repr__(self):
        return f"<MarketTrends(location='{self.location}', type='{self.property_type}', date={self.analysis_date})>"

# Create indexes for better query performance
Index('idx_properties_source_location', Property.source, Property.location)
Index('idx_properties_type_price', Property.property_type, Property.price)
Index('idx_properties_bedrooms_bathrooms', Property.bedrooms, Property.bathrooms)
Index('idx_properties_coordinates', Property.latitude, Property.longitude)
Index('idx_properties_crawled_at', Property.crawled_at)
Index('idx_properties_data_quality', Property.data_quality_score)

Index('idx_price_history_property_date', PropertyPriceHistory.property_id, PropertyPriceHistory.change_date)
Index('idx_similarities_score', PropertySimilarity.similarity_score)
Index('idx_crawl_sessions_source_status', CrawlSession.source, CrawlSession.status)
Index('idx_market_trends_location_type', MarketTrends.location, MarketTrends.property_type)
