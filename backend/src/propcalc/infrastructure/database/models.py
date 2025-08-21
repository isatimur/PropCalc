"""
SQLAlchemy models for PropCalc database
Modern models with Pydantic integration and best practices
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Integer, String, DateTime, Date, Boolean, Numeric, Text, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM
from pydantic import BaseModel, Field, ConfigDict
import uuid as uuid_lib

Base = declarative_base()

# Enums
class PropertyTypeEnum(str, Enum):
    APARTMENT = "Apartment"
    VILLA = "Villa"
    TOWNHOUSE = "Townhouse"
    OFFICE = "Office"
    RETAIL = "Retail"
    WAREHOUSE = "Warehouse"
    LAND = "Land"
    OTHER = "Other"

class TransactionTypeEnum(str, Enum):
    SALE = "Sale"
    RENT = "Rent"
    LEASE = "Lease"
    OTHER = "Other"

class DataSourceEnum(str, Enum):
    DLD_CSV = "DLD_CSV"
    DLD_API = "DLD_API"
    DLD_SCHEDULED = "DLD_SCHEDULED"
    MANUAL = "Manual"
    IMPORT = "Import"

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    DEVELOPER = "developer"

class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

# Pydantic Models for API
class DLDAreaBase(BaseModel):
    area_id: int = Field(..., description="Unique area identifier")
    name_en: str = Field(..., max_length=255, description="Area name in English")
    name_ar: str = Field(..., max_length=255, description="Area name in Arabic")
    municipality_number: Optional[str] = Field(None, max_length=10, description="Municipality number")

class DLDAreaCreate(DLDAreaBase):
    pass

class DLDArea(DLDAreaBase):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DLDTransactionBase(BaseModel):
    transaction_id: str = Field(..., max_length=255, description="Unique transaction identifier")
    property_type: PropertyTypeEnum = Field(..., description="Type of property")
    location: str = Field(..., max_length=255, description="Property location")
    transaction_date: datetime = Field(..., description="Transaction date")
    price_aed: Decimal = Field(..., ge=0, description="Transaction price in AED")
    area_sqft: Decimal = Field(..., gt=0, description="Property area in square feet")
    developer_name: Optional[str] = Field(None, max_length=255, description="Developer name")
    project_name: Optional[str] = Field(None, max_length=255, description="Project name")
    unit_number: Optional[str] = Field(None, max_length=50, description="Unit number")
    floor_number: Optional[int] = Field(None, ge=0, description="Floor number")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    parking_spaces: Optional[int] = Field(None, ge=0, description="Number of parking spaces")
    area_id: Optional[int] = Field(None, description="Reference to DLD area")

class DLDTransactionCreate(DLDTransactionBase):
    pass

class DLDTransaction(DLDTransactionBase):
    id: int
    uuid: uuid_lib.UUID
    market_type_id: Optional[int] = None
    procedure_id: Optional[int] = None
    quality_score: Optional[Decimal] = None
    data_source: DataSourceEnum = DataSourceEnum.DLD_CSV
    checksum: Optional[str] = None
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GeographicAreaBase(BaseModel):
    name: str = Field(..., max_length=255, description="Area name")
    name_arabic: Optional[str] = Field(None, max_length=255, description="Area name in Arabic")
    name_english: Optional[str] = Field(None, max_length=255, description="Area name in English")
    center_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Center latitude")
    center_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Center longitude")
    area_sqm: Optional[float] = Field(None, ge=0, description="Area in square meters")
    perimeter_m: Optional[float] = Field(None, ge=0, description="Perimeter in meters")
    polygon_coordinates: List[List[float]] = Field(default_factory=list, description="Polygon coordinates")

class GeographicAreaCreate(GeographicAreaBase):
    pass

class GeographicArea(GeographicAreaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AreaMarketStatisticsBase(BaseModel):
    area_id: int = Field(..., description="Reference to DLD area")
    geographic_area_id: Optional[int] = Field(None, description="Reference to geographic area")
    total_transactions: int = Field(0, ge=0, description="Total number of transactions")
    avg_price_aed: Optional[Decimal] = Field(None, ge=0, description="Average price in AED")
    avg_price_per_sqft: Optional[Decimal] = Field(None, ge=0, description="Average price per square foot")
    total_volume_aed: Optional[Decimal] = Field(None, ge=0, description="Total transaction volume in AED")
    property_types: Dict[str, int] = Field(default_factory=dict, description="Property type distribution")
    transaction_types: Dict[str, int] = Field(default_factory=dict, description="Transaction type distribution")

class AreaMarketStatisticsCreate(AreaMarketStatisticsBase):
    pass

class AreaMarketStatistics(AreaMarketStatisticsBase):
    id: int
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DLDKMLAreaMappingBase(BaseModel):
    dld_area_id: int = Field(..., description="Reference to DLD area")
    geographic_area_id: int = Field(..., description="Reference to geographic area")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Match confidence score")
    match_type: str = Field(..., max_length=50, description="Type of match (exact, fuzzy, partial)")
    match_criteria: Dict[str, Any] = Field(default_factory=dict, description="Match criteria details")

class DLDKMLAreaMappingCreate(DLDKMLAreaMappingBase):
    pass

class DLDKMLAreaMapping(DLDKMLAreaMappingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# SQLAlchemy Models
class DLDArea(Base):
    __tablename__ = "dld_areas"
    
    area_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    municipality_number: Mapped[Optional[str]] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    market_statistics: Mapped[List["AreaMarketStatistics"]] = relationship("AreaMarketStatistics", back_populates="area")
    kml_mappings: Mapped[List["DLDKMLAreaMapping"]] = relationship("DLDKMLAreaMapping", back_populates="dld_area")
    
    __table_args__ = (
        Index("idx_dld_areas_name_en", "name_en"),
        Index("idx_dld_areas_municipality", "municipality_number"),
    )

class DLDTransaction(Base):
    __tablename__ = "dld_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[uuid_lib.UUID] = mapped_column(PGUUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    property_type: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    area: Mapped[Optional[str]] = mapped_column(String(200))
    transaction_date: Mapped[Optional[date]] = mapped_column(Date)
    price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    area_sqft: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    price_per_sqft: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    developer_name: Mapped[Optional[str]] = mapped_column(String(200))
    project_name: Mapped[Optional[str]] = mapped_column(String(200))
    property_usage: Mapped[Optional[str]] = mapped_column(String(100))
    property_subtype: Mapped[Optional[str]] = mapped_column(String(100))
    rooms: Mapped[Optional[int]] = mapped_column(Integer)
    parking: Mapped[Optional[int]] = mapped_column(Integer)
    nearest_metro: Mapped[Optional[str]] = mapped_column(String(200))
    nearest_mall: Mapped[Optional[str]] = mapped_column(String(200))
    nearest_landmark: Mapped[Optional[str]] = mapped_column(String(200))
    registration_type: Mapped[Optional[str]] = mapped_column(String(100))
    buyer_nationality: Mapped[Optional[str]] = mapped_column(String(100))
    seller_nationality: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    processed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    data_source: Mapped[Optional[str]] = mapped_column(String(100), default="DLD_STREAM")
    
    # Relationships - no foreign key relationships exist in database schema
    
    __table_args__ = (
        Index("idx_dld_transactions_date", "transaction_date"),
        Index("idx_dld_transactions_developer", "developer_name"),
        Index("idx_dld_transactions_location", "location"),
        Index("idx_dld_transactions_price", "price_aed"),
        Index("idx_dld_transactions_data_source", "data_source"),
    )

class GeographicArea(Base):
    __tablename__ = "geographic_areas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_arabic: Mapped[Optional[str]] = mapped_column(String(255))
    name_english: Mapped[Optional[str]] = mapped_column(String(255))
    center_latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    center_longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    area_sqm: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    perimeter_m: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    polygon_coordinates: Mapped[Optional[List[List[float]]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    kml_mappings: Mapped[List["DLDKMLAreaMapping"]] = relationship("DLDKMLAreaMapping", back_populates="geographic_area")
    market_statistics: Mapped[List["AreaMarketStatistics"]] = relationship("AreaMarketStatistics", back_populates="geographic_area")
    
    __table_args__ = (
        Index("idx_geographic_areas_name", "name"),
        Index("idx_geographic_areas_coordinates", "center_latitude", "center_longitude"),
    )

class AreaMarketStatistics(Base):
    __tablename__ = "area_market_statistics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    area_id: Mapped[int] = mapped_column(Integer, ForeignKey("dld_areas.area_id"), unique=True)
    geographic_area_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("geographic_areas.id"))
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    avg_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    avg_price_per_sqft: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    total_volume_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    property_types: Mapped[Optional[Dict[str, int]]] = mapped_column(JSONB)
    transaction_types: Mapped[Optional[Dict[str, int]]] = mapped_column(JSONB)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area: Mapped["DLDArea"] = relationship("DLDArea", back_populates="market_statistics")
    geographic_area: Mapped[Optional["GeographicArea"]] = relationship("GeographicArea", back_populates="market_statistics")
    
    __table_args__ = (
        Index("idx_area_market_stats_area", "area_id"),
    )

class DLDKMLAreaMapping(Base):
    __tablename__ = "dld_kml_area_mapping"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dld_area_id: Mapped[int] = mapped_column(Integer, ForeignKey("dld_areas.area_id"))
    geographic_area_id: Mapped[int] = mapped_column(Integer, ForeignKey("geographic_areas.id"))
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    match_type: Mapped[str] = mapped_column(String(50))
    match_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dld_area: Mapped["DLDArea"] = relationship("DLDArea", back_populates="kml_mappings")
    geographic_area: Mapped["GeographicArea"] = relationship("GeographicArea", back_populates="kml_mappings")
    
    __table_args__ = (
        UniqueConstraint("dld_area_id", "geographic_area_id", name="uq_dld_kml_mapping"),
        Index("idx_dld_kml_mapping_dld_area", "dld_area_id"),
        Index("idx_dld_kml_mapping_geo_area", "geographic_area_id"),
    )

# Additional models for other tables
class Developer(Base):
    __tablename__ = "developers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_developers_name", "name"),
        Index("idx_developers_active", "is_active"),
    )

class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="api_usage")
    
    __table_args__ = (
        Index("idx_api_usage_endpoint", "endpoint"),
        Index("idx_api_usage_user_id", "user_id"),
        Index("idx_api_usage_created_at", "created_at"),
    )

# ============================================================================
# User and Authentication Models
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[uuid_lib.UUID] = mapped_column(PGUUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(ENUM(UserRoleEnum), default=UserRoleEnum.VIEWER)
    status: Mapped[UserStatusEnum] = mapped_column(ENUM(UserStatusEnum), default=UserStatusEnum.PENDING_VERIFICATION)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255))
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255))
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_usage: Mapped[List["APIUsage"]] = relationship("APIUsage", back_populates="user")
    
    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
        Index("idx_users_status", "status"),
        Index("idx_users_created_at", "created_at"),
    )

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    refresh_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index("idx_user_sessions_user_id", "user_id"),
        Index("idx_user_sessions_session_token", "session_token"),
        Index("idx_user_sessions_refresh_token", "refresh_token"),
        Index("idx_user_sessions_expires_at", "expires_at"),
    )

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    activity_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index("idx_user_activities_user_id", "user_id"),
        Index("idx_user_activities_activity_type", "activity_type"),
        Index("idx_user_activities_created_at", "created_at"),
    )

# ============================================================================
# Area Mapping and Region Hierarchy Models
# ============================================================================

class AreaMapping(Base):
    __tablename__ = "area_mapping"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dld_area_id: Mapped[Optional[str]] = mapped_column(String(10), ForeignKey("dld_areas_lookup.area_id"))
    dld_area_name: Mapped[Optional[str]] = mapped_column(String(200))
    internet_name: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(200), nullable=False)
    region_category: Mapped[Optional[str]] = mapped_column(String(100))
    municipality: Mapped[Optional[str]] = mapped_column(String(100))
    popularity_score: Mapped[int] = mapped_column(Integer, default=0)
    avg_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    min_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    max_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    price_trend: Mapped[Optional[str]] = mapped_column(String(50))
    transaction_volume: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dld_area: Mapped[Optional["DLDAreaLookup"]] = relationship("DLDAreaLookup", foreign_keys=[dld_area_id])
    analytics: Mapped[List["AreaAnalytics"]] = relationship("AreaAnalytics", back_populates="area_mapping")
    
    __table_args__ = (
        Index("idx_area_mapping_internet_name", "internet_name"),
        Index("idx_area_mapping_normalized_name", "normalized_name"),
        Index("idx_area_mapping_region_category", "region_category"),
        Index("idx_area_mapping_dld_area_name", "dld_area_name"),
    )

class RegionHierarchy(Base):
    __tablename__ = "region_hierarchy"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_region_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("region_hierarchy.id"))
    region_name: Mapped[str] = mapped_column(String(200), nullable=False)
    region_type: Mapped[Optional[str]] = mapped_column(String(100))
    level: Mapped[int] = mapped_column(Integer, default=1)
    coordinates_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    coordinates_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    bounding_box: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent_region: Mapped[Optional["RegionHierarchy"]] = relationship("RegionHierarchy", remote_side=[id])
    child_regions: Mapped[List["RegionHierarchy"]] = relationship("RegionHierarchy", back_populates="parent_region")
    
    __table_args__ = (
        Index("idx_region_hierarchy_parent", "parent_region_id"),
        Index("idx_region_hierarchy_type", "region_type"),
        Index("idx_region_hierarchy_level", "level"),
    )

class AreaAnalytics(Base):
    __tablename__ = "area_analytics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    area_mapping_id: Mapped[int] = mapped_column(Integer, ForeignKey("area_mapping.id"), nullable=False)
    analysis_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    total_volume_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    avg_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    median_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    min_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    max_price_aed: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    price_per_sqft_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    transaction_trend: Mapped[Optional[str]] = mapped_column(String(50))
    market_sentiment: Mapped[Optional[str]] = mapped_column(String(50))
    top_property_types: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    top_developers: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area_mapping: Mapped["AreaMapping"] = relationship("AreaMapping", back_populates="analytics")
    
    __table_args__ = (
        Index("idx_area_analytics_date", "analysis_date"),
        Index("idx_area_analytics_area", "area_mapping_id"),
        UniqueConstraint("area_mapping_id", "analysis_date", name="uq_area_analytics_date"),
    )

# Pydantic Models for Area Mapping API
class AreaMappingBase(BaseModel):
    dld_area_name: Optional[str] = Field(None, max_length=200, description="DLD area name")
    internet_name: str = Field(..., max_length=200, description="Internet-friendly area name")
    normalized_name: str = Field(..., max_length=200, description="Normalized area name for search")
    region_category: Optional[str] = Field(None, max_length=100, description="Region category")
    municipality: Optional[str] = Field(None, max_length=100, description="Municipality")
    popularity_score: int = Field(default=0, ge=0, le=100, description="Popularity score 0-100")

class AreaMappingCreate(AreaMappingBase):
    pass

class AreaMapping(AreaMappingBase):
    id: int
    dld_area_id: Optional[str] = None
    avg_price_aed: Optional[Decimal] = None
    min_price_aed: Optional[Decimal] = None
    max_price_aed: Optional[Decimal] = None
    price_trend: Optional[str] = None
    transaction_volume: int = 0
    last_updated: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AreaAnalyticsBase(BaseModel):
    analysis_date: datetime = Field(..., description="Analysis date")
    total_transactions: int = Field(default=0, ge=0, description="Total transactions")
    total_volume_aed: Optional[Decimal] = Field(None, ge=0, description="Total volume in AED")
    avg_price_aed: Optional[Decimal] = Field(None, ge=0, description="Average price in AED")
    median_price_aed: Optional[Decimal] = Field(None, ge=0, description="Median price in AED")
    min_price_aed: Optional[Decimal] = Field(None, ge=0, description="Minimum price in AED")
    max_price_aed: Optional[Decimal] = Field(None, ge=0, description="Maximum price in AED")
    price_per_sqft_avg: Optional[Decimal] = Field(None, ge=0, description="Average price per sqft")

class AreaAnalytics(AreaAnalyticsBase):
    id: int
    area_mapping_id: int
    transaction_trend: Optional[str] = None
    market_sentiment: Optional[str] = None
    top_property_types: Optional[Dict[str, Any]] = None
    top_developers: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RegionOverview(BaseModel):
    id: int
    dld_area_name: Optional[str] = None
    internet_name: str
    normalized_name: str
    region_category: Optional[str] = None
    municipality: Optional[str] = None
    popularity_score: int
    avg_price_aed: Optional[Decimal] = None
    min_price_aed: Optional[Decimal] = None
    max_price_aed: Optional[Decimal] = None
    price_trend: Optional[str] = None
    transaction_volume: int
    total_transactions: Optional[int] = None
    total_volume_aed: Optional[Decimal] = None
    median_price_aed: Optional[Decimal] = None
    price_per_sqft_avg: Optional[Decimal] = None
    market_sentiment: Optional[str] = None
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True) 