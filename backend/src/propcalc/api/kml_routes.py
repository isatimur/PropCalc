"""
API routes for KML data handling
Provides endpoints for area searches, mapping, and geographic information
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
from datetime import datetime

from ..core.kml_database_integration import KMLDatabaseIntegration
from ..infrastructure.database.postgres_db import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kml", tags=["KML Data"])

# Pydantic models for request/response
class AreaSearchRequest(BaseModel):
    search_term: str
    limit: Optional[int] = 50

class CoordinateSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = 10.0

class AreaResponse(BaseModel):
    id: int
    name: str
    name_arabic: Optional[str] = None
    name_english: Optional[str] = None
    sector_number: Optional[str] = None
    community_number: Optional[str] = None
    dgis_id: Optional[str] = None
    ndgis_id: Optional[str] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    area_sqm: Optional[float] = None
    perimeter_m: Optional[float] = None
    source_file: Optional[str] = None
    created_at: Optional[datetime] = None

class PointResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    source_file: Optional[str] = None
    created_at: Optional[datetime] = None

class AreaSearchResponse(BaseModel):
    areas: List[AreaResponse]
    total_count: int
    search_term: str

class CoordinateSearchResponse(BaseModel):
    areas: List[AreaResponse]
    points: List[PointResponse]
    total_areas: int
    total_points: int
    search_coordinates: Dict[str, float]
    radius_km: float

class SectorResponse(BaseModel):
    sector_number: str
    area_count: int
    sample_name: str

class CommunityResponse(BaseModel):
    community_number: str
    area_count: int
    sample_name: str

class StatisticsResponse(BaseModel):
    total_areas: int
    total_points: int
    total_lines: int
    area_statistics: Dict[str, Any]
    source_files: List[Dict[str, Any]]

def get_kml_db() -> KMLDatabaseIntegration:
    """Get KML database integration instance"""
    db_connection = get_db_connection()
    return KMLDatabaseIntegration(db_connection)

@router.get("/areas/search", response_model=AreaSearchResponse)
async def search_areas_by_name(
    search_term: str = Query(..., description="Search term for area names"),
    limit: int = Query(50, description="Maximum number of results"),
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Search areas by name (English or Arabic)"""
    try:
        areas = kml_db.search_areas_by_name(search_term, limit)
        
        return AreaSearchResponse(
            areas=[AreaResponse(**area) for area in areas],
            total_count=len(areas),
            search_term=search_term
        )
    except Exception as e:
        logger.error(f"Error searching areas by name: {e}")
        raise HTTPException(status_code=500, detail="Error searching areas")

@router.get("/areas/sector/{sector_number}", response_model=List[AreaResponse])
async def search_areas_by_sector(
    sector_number: str,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Search areas by sector number"""
    try:
        areas = kml_db.search_areas_by_sector(sector_number)
        return [AreaResponse(**area) for area in areas]
    except Exception as e:
        logger.error(f"Error searching areas by sector: {e}")
        raise HTTPException(status_code=500, detail="Error searching areas by sector")

@router.get("/areas/community/{community_number}", response_model=List[AreaResponse])
async def search_areas_by_community(
    community_number: str,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Search areas by community number"""
    try:
        areas = kml_db.search_areas_by_community(community_number)
        return [AreaResponse(**area) for area in areas]
    except Exception as e:
        logger.error(f"Error searching areas by community: {e}")
        raise HTTPException(status_code=500, detail="Error searching areas by community")

@router.post("/search/coordinates", response_model=CoordinateSearchResponse)
async def search_by_coordinates(
    request: CoordinateSearchRequest,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Search areas and points near given coordinates"""
    try:
        areas = kml_db.find_areas_near_coordinates(
            request.latitude, 
            request.longitude, 
            request.radius_km
        )
        points = kml_db.find_points_near_coordinates(
            request.latitude, 
            request.longitude, 
            request.radius_km
        )
        
        return CoordinateSearchResponse(
            areas=[AreaResponse(**area) for area in areas],
            points=[PointResponse(**point) for point in points],
            total_areas=len(areas),
            total_points=len(points),
            search_coordinates={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            radius_km=request.radius_km
        )
    except Exception as e:
        logger.error(f"Error searching by coordinates: {e}")
        raise HTTPException(status_code=500, detail="Error searching by coordinates")

@router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area_by_id(
    area_id: int,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get area by ID"""
    try:
        area = kml_db.get_area_by_id(area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        return AreaResponse(**area)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting area by ID: {e}")
        raise HTTPException(status_code=500, detail="Error getting area")

@router.get("/points/{point_id}", response_model=PointResponse)
async def get_point_by_id(
    point_id: int,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get point by ID"""
    try:
        point = kml_db.get_point_by_id(point_id)
        if not point:
            raise HTTPException(status_code=404, detail="Point not found")
        return PointResponse(**point)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting point by ID: {e}")
        raise HTTPException(status_code=500, detail="Error getting point")

@router.get("/sectors", response_model=List[SectorResponse])
async def get_all_sectors(
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get all unique sectors"""
    try:
        sectors = kml_db.get_all_sectors()
        return [SectorResponse(**sector) for sector in sectors]
    except Exception as e:
        logger.error(f"Error getting sectors: {e}")
        raise HTTPException(status_code=500, detail="Error getting sectors")

@router.get("/communities", response_model=List[CommunityResponse])
async def get_all_communities(
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get all unique communities"""
    try:
        communities = kml_db.get_all_communities()
        return [CommunityResponse(**community) for community in communities]
    except Exception as e:
        logger.error(f"Error getting communities: {e}")
        raise HTTPException(status_code=500, detail="Error getting communities")

@router.get("/statistics", response_model=StatisticsResponse)
async def get_area_statistics(
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get statistics about geographic areas"""
    try:
        stats = kml_db.get_area_statistics()
        return StatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting area statistics: {e}")
        raise HTTPException(status_code=500, detail="Error getting statistics")

@router.get("/areas/{area_id}/polygon")
async def get_area_polygon(
    area_id: int,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get polygon coordinates for an area"""
    try:
        area = kml_db.get_area_by_id(area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        
        # Parse polygon coordinates from JSON string
        import json
        polygon_coords = json.loads(area.get('polygon_coordinates', '[]'))
        
        return {
            "area_id": area_id,
            "area_name": area.get('name'),
            "coordinates": polygon_coords,
            "center": {
                "latitude": area.get('center_latitude'),
                "longitude": area.get('center_longitude')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting area polygon: {e}")
        raise HTTPException(status_code=500, detail="Error getting area polygon")

@router.get("/areas/{area_id}/nearby")
async def get_nearby_areas(
    area_id: int,
    radius_km: float = Query(5.0, description="Search radius in kilometers"),
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get areas near a specific area"""
    try:
        area = kml_db.get_area_by_id(area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        
        center_lat = area.get('center_latitude')
        center_lon = area.get('center_longitude')
        
        if not center_lat or not center_lon:
            raise HTTPException(status_code=400, detail="Area has no center coordinates")
        
        nearby_areas = kml_db.find_areas_near_coordinates(center_lat, center_lon, radius_km)
        
        # Remove the original area from results
        nearby_areas = [a for a in nearby_areas if a['id'] != area_id]
        
        return {
            "center_area": AreaResponse(**area),
            "nearby_areas": [AreaResponse(**a) for a in nearby_areas],
            "radius_km": radius_km,
            "total_nearby": len(nearby_areas)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting nearby areas: {e}")
        raise HTTPException(status_code=500, detail="Error getting nearby areas")

@router.get("/areas/{area_id}/points")
async def get_points_in_area(
    area_id: int,
    kml_db: KMLDatabaseIntegration = Depends(get_kml_db)
):
    """Get points within an area (approximate)"""
    try:
        area = kml_db.get_area_by_id(area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        
        center_lat = area.get('center_latitude')
        center_lon = area.get('center_longitude')
        area_sqm = area.get('area_sqm', 0)
        
        if not center_lat or not center_lon:
            raise HTTPException(status_code=400, detail="Area has no center coordinates")
        
        # Calculate approximate radius based on area
        import math
        radius_km = math.sqrt(area_sqm / 1000000 / math.pi) if area_sqm > 0 else 1.0
        
        points = kml_db.find_points_near_coordinates(center_lat, center_lon, radius_km)
        
        return {
            "area": AreaResponse(**area),
            "points": [PointResponse(**p) for p in points],
            "total_points": len(points),
            "search_radius_km": radius_km
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting points in area: {e}")
        raise HTTPException(status_code=500, detail="Error getting points in area")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KML API", "timestamp": datetime.now().isoformat()} 