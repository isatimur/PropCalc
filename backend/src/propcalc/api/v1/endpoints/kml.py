"""
KML API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from propcalc.infrastructure.database.database import get_async_db
from propcalc.infrastructure.repositories.dld_repository import (
    geographic_area_repo, dld_kml_mapping_repo
)

router = APIRouter()


@router.get("/areas")
async def get_geographic_areas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get geographic areas with optional search"""
    try:
        if search:
            return await geographic_area_repo.search_areas_async(db, search, limit)
        return await geographic_area_repo.get_multi_async(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving geographic areas: {str(e)}")


@router.get("/areas/{area_id}")
async def get_geographic_area(
    area_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get specific geographic area"""
    try:
        area = await geographic_area_repo.get_async(db, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Geographic area not found")
        return area
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving geographic area: {str(e)}")


@router.get("/mappings")
async def get_area_mappings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get DLD-KML area mappings"""
    try:
        if min_confidence > 0:
            return await dld_kml_mapping_repo.get_high_confidence_mappings_async(db, min_confidence)
        return await dld_kml_mapping_repo.get_multi_async(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area mappings: {str(e)}")


@router.get("/areas/{area_id}/mappings")
async def get_area_mappings_by_geographic_area(
    area_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get DLD mappings for a specific geographic area"""
    try:
        mappings = await dld_kml_mapping_repo.get_by_geographic_area_id_async(db, area_id)
        return {
            "geographic_area_id": area_id,
            "mappings": mappings,
            "total_mappings": len(mappings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area mappings: {str(e)}")


@router.get("/areas/with-coordinates")
async def get_areas_with_coordinates(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """Get geographic areas that have coordinates"""
    try:
        return await geographic_area_repo.get_areas_with_coordinates_async(db, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving areas with coordinates: {str(e)}")


@router.get("/areas/{area_id}/details")
async def get_area_details(
    area_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get comprehensive details for a geographic area including DLD mappings"""
    try:
        # Get geographic area
        area = await geographic_area_repo.get_async(db, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Geographic area not found")
        
        # Get DLD mappings
        mappings = await dld_kml_mapping_repo.get_by_geographic_area_id_async(db, area_id)
        
        return {
            "geographic_area": area,
            "dld_mappings": mappings,
            "total_dld_mappings": len(mappings),
            "has_coordinates": area.center_latitude is not None and area.center_longitude is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area details: {str(e)}") 