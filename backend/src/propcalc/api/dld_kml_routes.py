"""
API routes for DLD-KML integration
Provides location-based real estate analysis combining DLD transaction data with geographic areas
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
from datetime import datetime

from ..core.dld_kml_integration import DLDKMLIntegration
from ..infrastructure.database.postgres_db import get_db_connection
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dld-kml", tags=["DLD-KML Integration"])

# Pydantic models
class AreaMarketData(BaseModel):
    area_id: int
    name_en: str
    name_ar: str
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    area_sqm: Optional[float] = None
    perimeter_m: Optional[float] = None
    distance_km: Optional[float] = None
    market_statistics: Dict[str, Any] = {}

class AreaTransaction(BaseModel):
    transaction_id: str
    property_type: str
    location: str
    transaction_date: str
    price_aed: float
    area_sqft: float
    developer_name: Optional[str] = None
    project_name: Optional[str] = None

class AreaMatch(BaseModel):
    dld_area_id: int
    geographic_area_id: int
    confidence_score: float
    match_type: str
    dld_name: str
    geo_name: str

class LocationSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = 5.0

def get_dld_kml_integration() -> DLDKMLIntegration:
    """Get DLD-KML integration instance"""
    db_connection = get_db_connection()
    return DLDKMLIntegration(db_connection)

@router.post("/setup")
async def setup_integration(
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Setup DLD-KML integration tables and find area matches"""
    try:
        # Create integration tables
        dld_kml.create_integration_tables()
        
        # Find and save area matches
        matches = dld_kml.find_area_matches()
        dld_kml.save_area_matches(matches)
        
        return {
            "message": "DLD-KML integration setup completed",
            "matches_found": len(matches),
            "setup_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error setting up DLD-KML integration: {e}")
        raise HTTPException(status_code=500, detail="Error setting up integration")

@router.get("/areas/search/location", response_model=List[AreaMarketData])
async def search_areas_by_location(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometers"),
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Search areas by coordinates with market data"""
    try:
        areas = dld_kml.search_areas_by_location(latitude, longitude, radius_km)
        return [AreaMarketData(**area) for area in areas]
    except Exception as e:
        logger.error(f"Error searching areas by location: {e}")
        raise HTTPException(status_code=500, detail="Error searching areas")

@router.get("/areas/{area_id}/market-data")
async def get_area_market_data(
    area_id: int,
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Get market statistics for a specific area"""
    try:
        market_data = dld_kml.get_area_market_statistics(area_id)
        if not market_data:
            raise HTTPException(status_code=404, detail="Area not found")
        
        return market_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting area market data: {e}")
        raise HTTPException(status_code=500, detail="Error getting market data")

@router.get("/areas/{area_id}/transactions", response_model=List[AreaTransaction])
async def get_area_transactions(
    area_id: int,
    limit: int = Query(50, description="Maximum number of transactions"),
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Get recent transactions for an area"""
    try:
        transactions = dld_kml.get_area_transactions(area_id, limit)
        return [AreaTransaction(**transaction) for transaction in transactions]
    except Exception as e:
        logger.error(f"Error getting area transactions: {e}")
        raise HTTPException(status_code=500, detail="Error getting transactions")

@router.get("/areas/{area_id}/geographic-data")
async def get_area_geographic_data(
    area_id: int,
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Get geographic data for a DLD area"""
    try:
        geo_data = dld_kml.get_area_geographic_data(area_id)
        if not geo_data:
            raise HTTPException(status_code=404, detail="Geographic data not found")
        
        return geo_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting area geographic data: {e}")
        raise HTTPException(status_code=500, detail="Error getting geographic data")

@router.get("/matches", response_model=List[AreaMatch])
async def get_area_matches(
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Get all area matches between DLD and KML data"""
    try:
        with dld_kml.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    dkam.dld_area_id, dkam.geographic_area_id,
                    dkam.confidence_score, dkam.match_type,
                    da.name_en as dld_name,
                    ga.name_english as geo_name
                FROM dld_kml_area_mapping dkam
                JOIN dld_areas da ON dkam.dld_area_id = da.area_id
                JOIN geographic_areas ga ON dkam.geographic_area_id = ga.id
                ORDER BY dkam.confidence_score DESC
            """)
            
            matches = [dict(row) for row in cursor.fetchall()]
            return [AreaMatch(**match) for match in matches]
            
    except Exception as e:
        logger.error(f"Error getting area matches: {e}")
        raise HTTPException(status_code=500, detail="Error getting area matches")

@router.post("/update-market-statistics")
async def update_market_statistics(
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Update market statistics for all areas"""
    try:
        dld_kml.update_area_market_statistics()
        return {
            "message": "Market statistics updated successfully",
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating market statistics: {e}")
        raise HTTPException(status_code=500, detail="Error updating market statistics")

@router.get("/areas/{area_id}/nearby-areas")
async def get_nearby_areas(
    area_id: int,
    radius_km: float = Query(5.0, description="Search radius in kilometers"),
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Get nearby areas for a specific area"""
    try:
        # Get geographic data for the area
        geo_data = dld_kml.get_area_geographic_data(area_id)
        if not geo_data:
            raise HTTPException(status_code=404, detail="Area not found")
        
        # Search for nearby areas
        nearby_areas = dld_kml.search_areas_by_location(
            geo_data['center_latitude'],
            geo_data['center_longitude'],
            radius_km
        )
        
        # Remove the original area from results
        nearby_areas = [area for area in nearby_areas if area['area_id'] != area_id]
        
        return {
            "center_area": geo_data,
            "nearby_areas": nearby_areas,
            "radius_km": radius_km,
            "total_nearby": len(nearby_areas)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting nearby areas: {e}")
        raise HTTPException(status_code=500, detail="Error getting nearby areas")

@router.get("/market-insights")
async def get_market_insights(
    dld_kml: DLDKMLIntegration = Depends(get_dld_kml_integration)
):
    """Get overall market insights from DLD-KML integration"""
    try:
        with dld_kml.db.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get total areas with geographic data
            cursor.execute("""
                SELECT COUNT(DISTINCT da.area_id) as total_areas_with_geo,
                       COUNT(DISTINCT dkam.dld_area_id) as total_matched_areas
                FROM dld_areas da
                LEFT JOIN dld_kml_area_mapping dkam ON da.area_id = dkam.dld_area_id
            """)
            
            area_stats = cursor.fetchone()
            
            # Get transaction statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    AVG(price_aed) as avg_price_aed,
                    SUM(price_aed) as total_volume_aed,
                    COUNT(DISTINCT area_id) as areas_with_transactions
                FROM dld_transactions
                WHERE price_aed > 0
            """)
            
            transaction_stats = cursor.fetchone()
            
            # Get property type distribution
            cursor.execute("""
                SELECT property_type, COUNT(*) as count
                FROM dld_transactions
                WHERE property_type IS NOT NULL
                GROUP BY property_type
                ORDER BY count DESC
                LIMIT 10
            """)
            
            property_types = [dict(row) for row in cursor.fetchall()]
            
            return {
                "area_statistics": dict(area_stats) if area_stats else {},
                "transaction_statistics": dict(transaction_stats) if transaction_stats else {},
                "top_property_types": property_types,
                "generated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting market insights: {e}")
        raise HTTPException(status_code=500, detail="Error getting market insights")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "DLD-KML Integration API", 
        "timestamp": datetime.now().isoformat()
    } 