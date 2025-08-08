"""
DLD-specific repositories for PropCalc
Repository pattern implementation for DLD entities
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .base import CRUDRepository
from ..database.models import (
    DLDArea, DLDTransaction, GeographicArea, AreaMarketStatistics, 
    DLDKMLAreaMapping, PropertyTypeEnum, DataSourceEnum
)
from ..database.models import (
    DLDAreaCreate, DLDArea as DLDAreaSchema,
    DLDTransactionCreate, DLDTransaction as DLDTransactionSchema,
    GeographicAreaCreate, GeographicArea as GeographicAreaSchema,
    AreaMarketStatisticsCreate, AreaMarketStatistics as AreaMarketStatisticsSchema,
    DLDKMLAreaMappingCreate, DLDKMLAreaMapping as DLDKMLAreaMappingSchema
)


class DLDAreaRepository(CRUDRepository[DLDArea, DLDAreaCreate, DLDAreaSchema]):
    """Repository for DLD Areas"""
    
    def __init__(self):
        super().__init__(DLDArea)
    
    def get_by_area_id(self, db: Session, area_id: int) -> Optional[DLDArea]:
        """Get area by DLD area_id"""
        return db.query(DLDArea).filter(DLDArea.area_id == area_id).first()
    
    async def get_by_area_id_async(self, db: AsyncSession, area_id: int) -> Optional[DLDArea]:
        """Get area by DLD area_id (async)"""
        result = await db.execute(select(DLDArea).filter(DLDArea.area_id == area_id))
        return result.scalar_one_or_none()
    
    def get_by_name(self, db: Session, name: str, language: str = "en") -> Optional[DLDArea]:
        """Get area by name in specified language"""
        if language == "ar":
            return db.query(DLDArea).filter(DLDArea.name_ar == name).first()
        return db.query(DLDArea).filter(DLDArea.name_en == name).first()
    
    async def get_by_name_async(self, db: AsyncSession, name: str, language: str = "en") -> Optional[DLDArea]:
        """Get area by name in specified language (async)"""
        if language == "ar":
            result = await db.execute(select(DLDArea).filter(DLDArea.name_ar == name))
        else:
            result = await db.execute(select(DLDArea).filter(DLDArea.name_en == name))
        return result.scalar_one_or_none()
    
    def search_areas(self, db: Session, search_term: str, limit: int = 50) -> List[DLDArea]:
        """Search areas by name (English or Arabic)"""
        search_pattern = f"%{search_term}%"
        return db.query(DLDArea).filter(
            or_(
                DLDArea.name_en.ilike(search_pattern),
                DLDArea.name_ar.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    async def search_areas_async(self, db: AsyncSession, search_term: str, limit: int = 50) -> List[DLDArea]:
        """Search areas by name (English or Arabic) (async)"""
        search_pattern = f"%{search_term}%"
        result = await db.execute(
            select(DLDArea).filter(
                or_(
                    DLDArea.name_en.ilike(search_pattern),
                    DLDArea.name_ar.ilike(search_pattern)
                )
            ).limit(limit)
        )
        return result.scalars().all()
    
    def get_areas_with_transactions(self, db: Session, limit: int = 100) -> List[DLDArea]:
        """Get areas that have transactions"""
        return db.query(DLDArea).join(DLDTransaction).distinct().limit(limit).all()
    
    async def get_areas_with_transactions_async(self, db: AsyncSession, limit: int = 100) -> List[DLDArea]:
        """Get areas that have transactions (async)"""
        result = await db.execute(
            select(DLDArea).join(DLDTransaction).distinct().limit(limit)
        )
        return result.scalars().all()


class DLDTransactionRepository(CRUDRepository[DLDTransaction, DLDTransactionCreate, DLDTransactionSchema]):
    """Repository for DLD Transactions"""
    
    def __init__(self):
        super().__init__(DLDTransaction)
    
    def get_by_transaction_id(self, db: Session, transaction_id: str) -> Optional[DLDTransaction]:
        """Get transaction by DLD transaction_id"""
        return db.query(DLDTransaction).filter(DLDTransaction.transaction_id == transaction_id).first()
    
    async def get_by_transaction_id_async(self, db: AsyncSession, transaction_id: str) -> Optional[DLDTransaction]:
        """Get transaction by DLD transaction_id (async)"""
        result = await db.execute(select(DLDTransaction).filter(DLDTransaction.transaction_id == transaction_id))
        return result.scalar_one_or_none()
    
    def get_by_area(self, db: Session, area_id: int, limit: int = 100) -> List[DLDTransaction]:
        """Get transactions for a specific area"""
        return db.query(DLDTransaction).filter(
            DLDTransaction.area_id == area_id
        ).order_by(desc(DLDTransaction.transaction_date)).limit(limit).all()
    
    async def get_by_area_async(self, db: AsyncSession, area_id: int, limit: int = 100) -> List[DLDTransaction]:
        """Get transactions for a specific area (async)"""
        result = await db.execute(
            select(DLDTransaction).filter(DLDTransaction.area_id == area_id)
            .order_by(desc(DLDTransaction.transaction_date)).limit(limit)
        )
        return result.scalars().all()
    
    def get_by_date_range(
        self, 
        db: Session, 
        start_date: date, 
        end_date: date, 
        limit: int = 1000
    ) -> List[DLDTransaction]:
        """Get transactions within a date range"""
        return db.query(DLDTransaction).filter(
            and_(
                DLDTransaction.transaction_date >= start_date,
                DLDTransaction.transaction_date <= end_date
            )
        ).order_by(desc(DLDTransaction.transaction_date)).limit(limit).all()
    
    async def get_by_date_range_async(
        self, 
        db: AsyncSession, 
        start_date: date, 
        end_date: date, 
        limit: int = 1000
    ) -> List[DLDTransaction]:
        """Get transactions within a date range (async)"""
        result = await db.execute(
            select(DLDTransaction).filter(
                and_(
                    DLDTransaction.transaction_date >= start_date,
                    DLDTransaction.transaction_date <= end_date
                )
            ).order_by(desc(DLDTransaction.transaction_date)).limit(limit)
        )
        return result.scalars().all()
    
    def get_by_property_type(self, db: Session, property_type: PropertyTypeEnum, limit: int = 1000) -> List[DLDTransaction]:
        """Get transactions by property type"""
        return db.query(DLDTransaction).filter(
            DLDTransaction.property_type == property_type
        ).order_by(desc(DLDTransaction.transaction_date)).limit(limit).all()
    
    async def get_by_property_type_async(self, db: AsyncSession, property_type: PropertyTypeEnum, limit: int = 1000) -> List[DLDTransaction]:
        """Get transactions by property type (async)"""
        result = await db.execute(
            select(DLDTransaction).filter(DLDTransaction.property_type == property_type)
            .order_by(desc(DLDTransaction.transaction_date)).limit(limit)
        )
        return result.scalars().all()
    
    def get_by_developer(self, db: Session, developer_name: str, limit: int = 1000) -> List[DLDTransaction]:
        """Get transactions by developer"""
        return db.query(DLDTransaction).filter(
            DLDTransaction.developer_name == developer_name
        ).order_by(desc(DLDTransaction.transaction_date)).limit(limit).all()
    
    async def get_by_developer_async(self, db: AsyncSession, developer_name: str, limit: int = 1000) -> List[DLDTransaction]:
        """Get transactions by developer (async)"""
        result = await db.execute(
            select(DLDTransaction).filter(DLDTransaction.developer_name == developer_name)
            .order_by(desc(DLDTransaction.transaction_date)).limit(limit)
        )
        return result.scalars().all()
    
    def get_market_statistics(self, db: Session, area_id: Optional[int] = None) -> Dict[str, Any]:
        """Get market statistics for transactions"""
        query = db.query(
            func.count(DLDTransaction.id).label('total_transactions'),
            func.avg(DLDTransaction.price_aed).label('avg_price'),
            func.sum(DLDTransaction.price_aed).label('total_volume'),
            func.avg(DLDTransaction.area_sqft).label('avg_area'),
            func.avg(DLDTransaction.price_aed / DLDTransaction.area_sqft).label('avg_price_per_sqft')
        )
        
        if area_id:
            query = query.filter(DLDTransaction.area_id == area_id)
        
        result = query.first()
        return {
            'total_transactions': result.total_transactions or 0,
            'avg_price': float(result.avg_price) if result.avg_price else 0,
            'total_volume': float(result.total_volume) if result.total_volume else 0,
            'avg_area': float(result.avg_area) if result.avg_area else 0,
            'avg_price_per_sqft': float(result.avg_price_per_sqft) if result.avg_price_per_sqft else 0
        }
    
    async def get_market_statistics_async(self, db: AsyncSession, area_id: Optional[int] = None) -> Dict[str, Any]:
        """Get market statistics for transactions (async)"""
        query = select(
            func.count(DLDTransaction.id).label('total_transactions'),
            func.avg(DLDTransaction.price_aed).label('avg_price'),
            func.sum(DLDTransaction.price_aed).label('total_volume'),
            func.avg(DLDTransaction.area_sqft).label('avg_area'),
            func.avg(DLDTransaction.price_aed / DLDTransaction.area_sqft).label('avg_price_per_sqft')
        )
        
        if area_id:
            query = query.filter(DLDTransaction.area_id == area_id)
        
        result = await db.execute(query)
        row = result.first()
        return {
            'total_transactions': row.total_transactions or 0,
            'avg_price': float(row.avg_price) if row.avg_price else 0,
            'total_volume': float(row.total_volume) if row.total_volume else 0,
            'avg_area': float(row.avg_area) if row.avg_area else 0,
            'avg_price_per_sqft': float(row.avg_price_per_sqft) if row.avg_price_per_sqft else 0
        }


class GeographicAreaRepository(CRUDRepository[GeographicArea, GeographicAreaCreate, GeographicAreaSchema]):
    """Repository for Geographic Areas"""
    
    def __init__(self):
        super().__init__(GeographicArea)
    
    def get_by_name(self, db: Session, name: str) -> Optional[GeographicArea]:
        """Get geographic area by name"""
        return db.query(GeographicArea).filter(GeographicArea.name == name).first()
    
    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[GeographicArea]:
        """Get geographic area by name (async)"""
        result = await db.execute(select(GeographicArea).filter(GeographicArea.name == name))
        return result.scalar_one_or_none()
    
    def search_areas(self, db: Session, search_term: str, limit: int = 50) -> List[GeographicArea]:
        """Search geographic areas by name"""
        search_pattern = f"%{search_term}%"
        return db.query(GeographicArea).filter(
            or_(
                GeographicArea.name.ilike(search_pattern),
                GeographicArea.name_english.ilike(search_pattern),
                GeographicArea.name_arabic.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    async def search_areas_async(self, db: AsyncSession, search_term: str, limit: int = 50) -> List[GeographicArea]:
        """Search geographic areas by name (async)"""
        search_pattern = f"%{search_term}%"
        result = await db.execute(
            select(GeographicArea).filter(
                or_(
                    GeographicArea.name.ilike(search_pattern),
                    GeographicArea.name_english.ilike(search_pattern),
                    GeographicArea.name_arabic.ilike(search_pattern)
                )
            ).limit(limit)
        )
        return result.scalars().all()
    
    def get_areas_with_coordinates(self, db: Session, limit: int = 100) -> List[GeographicArea]:
        """Get areas that have coordinates"""
        return db.query(GeographicArea).filter(
            and_(
                GeographicArea.center_latitude.isnot(None),
                GeographicArea.center_longitude.isnot(None)
            )
        ).limit(limit).all()
    
    async def get_areas_with_coordinates_async(self, db: AsyncSession, limit: int = 100) -> List[GeographicArea]:
        """Get areas that have coordinates (async)"""
        result = await db.execute(
            select(GeographicArea).filter(
                and_(
                    GeographicArea.center_latitude.isnot(None),
                    GeographicArea.center_longitude.isnot(None)
                )
            ).limit(limit)
        )
        return result.scalars().all()


class AreaMarketStatisticsRepository(CRUDRepository[AreaMarketStatistics, AreaMarketStatisticsCreate, AreaMarketStatisticsSchema]):
    """Repository for Area Market Statistics"""
    
    def __init__(self):
        super().__init__(AreaMarketStatistics)
    
    def get_by_area_id(self, db: Session, area_id: int) -> Optional[AreaMarketStatistics]:
        """Get market statistics by area ID"""
        return db.query(AreaMarketStatistics).filter(AreaMarketStatistics.area_id == area_id).first()
    
    async def get_by_area_id_async(self, db: AsyncSession, area_id: int) -> Optional[AreaMarketStatistics]:
        """Get market statistics by area ID (async)"""
        result = await db.execute(select(AreaMarketStatistics).filter(AreaMarketStatistics.area_id == area_id))
        return result.scalar_one_or_none()
    
    def get_top_performing_areas(self, db: Session, limit: int = 10) -> List[AreaMarketStatistics]:
        """Get top performing areas by transaction volume"""
        return db.query(AreaMarketStatistics).filter(
            AreaMarketStatistics.total_volume_aed.isnot(None)
        ).order_by(desc(AreaMarketStatistics.total_volume_aed)).limit(limit).all()
    
    async def get_top_performing_areas_async(self, db: AsyncSession, limit: int = 10) -> List[AreaMarketStatistics]:
        """Get top performing areas by transaction volume (async)"""
        result = await db.execute(
            select(AreaMarketStatistics).filter(AreaMarketStatistics.total_volume_aed.isnot(None))
            .order_by(desc(AreaMarketStatistics.total_volume_aed)).limit(limit)
        )
        return result.scalars().all()


class DLDKMLAreaMappingRepository(CRUDRepository[DLDKMLAreaMapping, DLDKMLAreaMappingCreate, DLDKMLAreaMappingSchema]):
    """Repository for DLD-KML Area Mappings"""
    
    def __init__(self):
        super().__init__(DLDKMLAreaMapping)
    
    def get_by_dld_area_id(self, db: Session, dld_area_id: int) -> List[DLDKMLAreaMapping]:
        """Get mappings by DLD area ID"""
        return db.query(DLDKMLAreaMapping).filter(DLDKMLAreaMapping.dld_area_id == dld_area_id).all()
    
    async def get_by_dld_area_id_async(self, db: AsyncSession, dld_area_id: int) -> List[DLDKMLAreaMapping]:
        """Get mappings by DLD area ID (async)"""
        result = await db.execute(select(DLDKMLAreaMapping).filter(DLDKMLAreaMapping.dld_area_id == dld_area_id))
        return result.scalars().all()
    
    def get_by_geographic_area_id(self, db: Session, geographic_area_id: int) -> List[DLDKMLAreaMapping]:
        """Get mappings by geographic area ID"""
        return db.query(DLDKMLAreaMapping).filter(DLDKMLAreaMapping.geographic_area_id == geographic_area_id).all()
    
    async def get_by_geographic_area_id_async(self, db: AsyncSession, geographic_area_id: int) -> List[DLDKMLAreaMapping]:
        """Get mappings by geographic area ID (async)"""
        result = await db.execute(select(DLDKMLAreaMapping).filter(DLDKMLAreaMapping.geographic_area_id == geographic_area_id))
        return result.scalars().all()
    
    def get_high_confidence_mappings(self, db: Session, min_confidence: float = 0.8) -> List[DLDKMLAreaMapping]:
        """Get mappings with high confidence scores"""
        return db.query(DLDKMLAreaMapping).filter(
            DLDKMLAreaMapping.confidence_score >= min_confidence
        ).order_by(desc(DLDKMLAreaMapping.confidence_score)).all()
    
    async def get_high_confidence_mappings_async(self, db: AsyncSession, min_confidence: float = 0.8) -> List[DLDKMLAreaMapping]:
        """Get mappings with high confidence scores (async)"""
        result = await db.execute(
            select(DLDKMLAreaMapping).filter(DLDKMLAreaMapping.confidence_score >= min_confidence)
            .order_by(desc(DLDKMLAreaMapping.confidence_score))
        )
        return result.scalars().all()


# Repository instances
dld_area_repo = DLDAreaRepository()
dld_transaction_repo = DLDTransactionRepository()
geographic_area_repo = GeographicAreaRepository()
area_market_stats_repo = AreaMarketStatisticsRepository()
dld_kml_mapping_repo = DLDKMLAreaMappingRepository() 