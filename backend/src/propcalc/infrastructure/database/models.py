"""
SQLAlchemy models for PropCalc database
Modern models with Pydantic integration and best practices
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Integer, String, DateTime, Boolean, Numeric, Text, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM
from pydantic import BaseModel, Field, ConfigDict
import uuid

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
    uuid: uuid.UUID
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
    transactions: Mapped[List["DLDTransaction"]] = relationship("DLDTransaction", back_populates="area")
    market_statistics: Mapped[List["AreaMarketStatistics"]] = relationship("AreaMarketStatistics", back_populates="area")
    kml_mappings: Mapped[List["DLDKMLAreaMapping"]] = relationship("DLDKMLAreaMapping", back_populates="dld_area")
    
    __table_args__ = (
        Index("idx_dld_areas_name_en", "name_en"),
        Index("idx_dld_areas_municipality", "municipality_number"),
    )

class DLDTransaction(Base):
    __tablename__ = "dld_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    property_type: Mapped[PropertyTypeEnum] = mapped_column(ENUM(PropertyTypeEnum), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price_aed: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    area_sqft: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    developer_name: Mapped[Optional[str]] = mapped_column(String(255))
    project_name: Mapped[Optional[str]] = mapped_column(String(255))
    unit_number: Mapped[Optional[str]] = mapped_column(String(50))
    floor_number: Mapped[Optional[int]] = mapped_column(Integer)
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer)
    parking_spaces: Mapped[Optional[int]] = mapped_column(Integer)
    area_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dld_areas.area_id"))
    market_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    procedure_id: Mapped[Optional[int]] = mapped_column(Integer)
    quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    data_source: Mapped[DataSourceEnum] = mapped_column(ENUM(DataSourceEnum), default=DataSourceEnum.DLD_CSV)
    checksum: Mapped[Optional[str]] = mapped_column(String(64))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    area: Mapped[Optional["DLDArea"]] = relationship("DLDArea", back_populates="transactions")
    
    __table_args__ = (
        Index("idx_dld_transactions_area", "area_id"),
        Index("idx_dld_transactions_date", "transaction_date"),
        Index("idx_dld_transactions_developer", "developer_name"),
        Index("idx_dld_transactions_location", "location"),
        Index("idx_dld_transactions_price", "price_aed"),
        Index("idx_dld_transactions_quality", "quality_score"),
        Index("idx_dld_transactions_verified", "is_verified"),
        CheckConstraint("price_aed > 0", name="dld_transactions_price_aed_check"),
        CheckConstraint("area_sqft > 0", name="dld_transactions_area_sqft_check"),
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
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_api_usage_endpoint", "endpoint"),
        Index("idx_api_usage_user", "user_id"),
        Index("idx_api_usage_created", "created_at"),
    ) 